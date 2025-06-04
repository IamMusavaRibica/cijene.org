import requests
from loguru import logger

from cijenelib.fetchers._common import get_csv_rows, cached_fetch, resolve_product
from cijenelib.models import Store
from lxml.etree import HTML

from cijenelib.utils import fix_address, fix_city


def fetch_ntl_prices(ntl: Store):
    root0 = HTML(requests.get('https://www.ntl.hr/cjenici-za-ntl-supermarkete').content)
    hrefs = []
    for href in root0.xpath('//a[contains(@href, ".csv")]/@href'):
        h = href.removeprefix('https://www.ntl.hr/csv_files/')
        market_type, address, city, store_id, *rest = h.split('_')
        if not (store_id.isdigit() and len(store_id) == 5):
            print(f'failed to parse store id from {h}')
            continue
        city = fix_city(city)
        hrefs.append((href, fix_address(address), city, store_id))

    if not hrefs:
        logger.warning(f'no prices found for ntl')
        return []

    prod = []
    for url, address, city, store_id in hrefs:
        if store_id not in ntl.locations:
            ntl.locations[store_id] = [city, None, address, None, None, None]

        logger.debug(f'fetching {url} for ntl {store_id}, {address}, {city}')
        rows = get_csv_rows(cached_fetch(url), delimiter=';', encoding='cp1250')
        for k in rows[1:]:
            name, _id, brand, _qty, units, mpc, ppu, discount_mpc, last_30d_mpc, may2_price, barcode, category = k
            if not barcode:
                continue

            name = name.strip().replace('0 ,5L', '0,5L')
            price = float('0' + (discount_mpc or mpc).replace(',', '.'))
            may2_price = float('0' + may2_price.replace(',', '.')) if may2_price else None

            resolve_product(prod, barcode, ntl, store_id, name, price, None, may2_price)

    return prod