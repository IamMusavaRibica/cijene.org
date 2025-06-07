from datetime import datetime
from urllib.parse import unquote

from loguru import logger
from lxml.etree import XML

from cijenelib.fetchers._archiver import WaybackArchiver, Pricelist
from cijenelib.fetchers._common import xpath, ensure_archived, resolve_product
from cijenelib.models import Store
from cijenelib.utils import fix_address, fix_city, UA_HEADER


def fetch_bure_prices(bure: Store):
    WaybackArchiver.archive(index_url := 'https://www.bure.hr/cjenici-arhiva')
    coll = []
    for href in xpath(index_url, '//a[contains(@href, ".xml")]/@href', extra_headers=UA_HEADER):
        filename = unquote(href.rsplit('/', 1)[-1])
        market_type, address, location_id, file_id, rest = filename.split('-', 4)
        i = 3 if address.endswith('BIOGRAD_NA_MORU') else 1
        address, *city = address.rsplit('_', i)
        address = fix_address(address.replace('_', ' '))
        city = fix_city(' '.join(city))
        dt = datetime.strptime(rest.replace('-', '')[:14], '%Y%m%d%H%M%S')
        coll.append(p := Pricelist(href, address, city, bure.id, location_id, dt, filename))
        p.request_kwargs = {'headers': UA_HEADER}

    if not coll:
        logger.warning('no bure prices found')
        return []

    logger.info(f'found {len(coll)} bure pricelists')
    coll.sort(key=lambda x: x.dt, reverse=True)
    today = coll[0].dt.date()
    today_coll = []
    for p in coll:
        if p.dt.date() == today:
            today_coll.append(p)
        else:
            ensure_archived(p, wayback=False)


    prod = []
    for p in today_coll:
        root = XML(ensure_archived(p, True, wayback=False))
        for prodajni_objekt in root.findall('ProdajniObjekt'):
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
                resolve_product(prod, barcode, bure, p.location_id, name, discount_mpc or mpc, _qty, may2_price)

    return prod