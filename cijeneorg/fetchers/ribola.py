import re
from datetime import datetime, date

from loguru import logger
from lxml.etree import XML

from cijeneorg.fetchers.archiver import WaybackArchiver, PriceList
from cijeneorg.fetchers.common import resolve_product, xpath, ensure_archived, extract_offers_since
from cijeneorg.models import Store
from cijeneorg.products import AllProducts
from cijeneorg.utils import remove_extra_spaces

BASE_URL = 'https://ribola.hr/ribola-cjenici/'


def fetch_ribola_prices(ribola: Store, min_date: date):
    WaybackArchiver.archive(BASE_URL)
    WaybackArchiver.archive('https://ribola.hr/cjenici/')
    coll = []

    hrefs = set()
    for date_url in xpath(BASE_URL, '//a[starts-with(@href, "?date=")]/@href'):
        full_url = BASE_URL + date_url

        day, month, year = map(int, date_url.rsplit('?date=')[-1].split('.'))
        date_ = date(year, month, day)
        if date_ >= min_date:
            WaybackArchiver.archive(full_url)
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

                _now = datetime.now()
                if _now.month <= 2 and _now.year == 2026 and dt.month == 12 and dt.year == 2026 and dt.day in {28, 29}:
                    dt = dt.replace(year=2025)

                if m:
                    location_id = m.group(1)
                    if location_id in ribola.locations:
                        loc = ribola.locations[location_id]
                        filename = href.rsplit('/')[-1]
                        coll.append(PriceList(BASE_URL + href, loc.address, loc.city, ribola.id, location_id, dt, filename))
                        continue
                    else:
                        logger.warning(f'unknown ribola location id: {location_id} from {href}')
                logger.warning(f'failed to parse ribola href: {href}')

    actual = extract_offers_since(ribola, coll, min_date)

    prod = []
    for p in actual:
        try:
            prod.extend(process_single(p, ribola))
        except Exception as e:
            logger.error(f'error processing ribola pricelist {p.url}: {e!r}')
    return prod


def process_single(p: PriceList, ribola: Store):
    root = XML(ensure_archived(p, True, wayback=False)
               .replace(b'MaloprmdajnaCijenaAkcija', b'MaloprodajnaCijenaAkcija'))
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

            # try:
            #     *_, _qty, unit = name.rsplit(maxsplit=2)
            #     quantity = float(_qty.replace(',', '.'))
            # except ValueError:  # can be thrown when unpacking or converting to float fails
            #     if barcode in AllProducts:
            #         logger.warning(f'didnt parse product {barcode} `{name}` {_qty =}')

            resolve_product(coll, barcode, ribola, location_id, name, brand, discount_mpc or mpc, _qty, may2_price, p.date)
    return coll
