import re
from datetime import datetime

import requests
from loguru import logger
from lxml.etree import HTML, XML, tostring

from cijenelib.fetchers._archiver import WaybackArchiver, Pricelist
from cijenelib.fetchers._common import cached_fetch, resolve_product, xpath, ensure_archived
from cijenelib.models import Store
from cijenelib.products import AllProducts
from cijenelib.utils import remove_extra_spaces

BASE_URL = 'https://ribola.hr/ribola-cjenici/'
def fetch_ribola_prices(ribola: Store):
    WaybackArchiver.archive(BASE_URL)
    coll = []

    hrefs = set()
    for date_url in xpath(BASE_URL, '//a[starts-with(@href, "?date=")]/@href'):
        WaybackArchiver.archive(full_url := BASE_URL + date_url)
        for href in xpath(full_url, '//a[@download]/@href'):
            if href not in hrefs:  # avoid duplicates
                hrefs.add(href)
                # market_type, full_addr, location_id, _ = href.split('-', 3)
                m = re.search(r'-(\d\d\d)-\d+-(20\d\d-[01]\d-[0123]\d-[012]\d-\d\d-\d\d)-', href)
                if not m:
                    m = re.search(r'-(\d\d\d)-\d+-(20\d\d[01]\d[0123]\d[012]\d\d\d\d\d)', href)
                    dt = m and datetime.strptime(m.group(2), '%Y%m%d%H%M%S')
                else:
                    dt = datetime.strptime(m.group(2), '%Y-%m-%d-%H-%M-%S')

                if m:
                    location_id = m.group(1)
                    if location_id in ribola.locations:
                        city, _, address, lat, lon, gmaps_url = ribola.locations[location_id]
                        filename = href.rsplit('/')[-1]
                        coll.append(Pricelist(BASE_URL + href, address, city, ribola.id, location_id, dt, filename))
                        continue
                    else:
                        logger.warning(f'unknown ribola location id: {location_id} from {href}')
                logger.warning(f'failed to parse ribola href: {href}')


    if not coll:
        logger.error('no ribola pricelists found')
        return []

    logger.info(f'found {len(coll)} ribola pricelists')
    coll.sort(key=lambda x: x.dt, reverse=True)
    today = coll[0].dt.date()
    today_coll = []
    for p in coll:
        if p.dt.date() == today:
            today_coll.append(p)
        else:
            ensure_archived(p)

    prod = []
    for p in today_coll:
        try:
            prod.extend(process_single(p, ribola))
        except Exception as e:
            logger.error(f'error processing ribola pricelist {p.url}: {e!r}')
    return prod


def process_single(p: Pricelist, ribola: Store):
    root = XML(ensure_archived(p, True).replace(b'MaloprmdajnaCijenaAkcija', b'MaloprodajnaCijenaAkcija'))
    coll = []
    for prodajni_objekt in root.findall('ProdajniObjekt'):
        location_id = prodajni_objekt.findtext('Oznaka')
        for k in prodajni_objekt.find('Proizvodi').findall('Proizvod'):
            name: str = k.findtext('NazivProizvoda')
            _id = k.findtext('SifraProizvoda')
            brand = k.findtext('MarkaProizvoda')
            _qty = k.findtext('NetoKolicina')
            unit = k.findtext('JedinicaMjere')
            mpc = k.findtext('MaloprodajnaCijena')
            ppu = k.findtext('CijenaZaJedinicuMjere')
            discount_mpc = k.findtext('MaloprodajnaCijenaAkcija')
            last_30d_mpc = k.findtext('NajnizaCijena')
            may2_price = k.findtext('SidrenaCijena')
            barcode = k.findtext('Barkod')
            category = k.findtext('KategorijeProizvoda')

            while '  ' in name:
                name = name.replace('  ', ' ')

            name = (remove_extra_spaces(name).strip()
                    .replace('GA ZIRANI', 'GAZIRANI')
                    .replace('G AZIRANI', 'GAZIRANI')
                    .replace(' P ET', ' PET')
                    .replace(' PE T', ' PET')
                    .replace('lE T GAZIRANI SOK', 'l PET GAZIRANI SOK')
                    .replace('lE T', 'l PET')
                    .replace('0, 5', '0,5'))

            if name.endswith('l P'):
                name = name[:-3] + 'l PET'

            name = (name.replace(' PET GAZIRANI SOK', '')
                .replace(' PET GAZIRANI S', '')
                .replace(' l PET', ' l')
                .replace(' l P', ' l')
                .replace(' 5+1 GRATIS LIM.', '')
                .replace(' GAZIRANI SOK', ''))

            try:
                *_, _qty, unit = name.rsplit(maxsplit=2)
                quantity = float(_qty.replace(',', '.'))
            except ValueError:  # can be thrown when unpacking or converting to float fails
                if barcode in AllProducts:
                    logger.warning(f'didnt parse product {barcode} `{name}` {_qty =}')

            resolve_product(coll, barcode, ribola, location_id, name, discount_mpc or mpc, _qty, may2_price)
    return coll