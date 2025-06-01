from loguru import logger

from cijenelib.fetchers.common import get_csv_rows, cached_fetch, resolve_product
from cijenelib.models import Store

import requests
from lxml.etree import HTML, tostring

from cijenelib.products import AllProducts
from cijenelib.utils import fix_address, fix_city


def fetch_boso_prices(boso: Store):
    root0 = HTML(requests.get('https://www.boso.hr/cjenik/').content)

    hrefs = []
    for tr in root0.xpath('//a[contains(@href, "uploads/cjenik")]/../..'):
        # we extract from filename because it has store id
        _, filename_td, date_td, anchor_td = tr.getchildren()
        market_type, address, city, rest = filename_td.text.split(', ')
        store_id, *_ = rest.split(',', 1)
        if not (store_id.isdigit() and len(store_id) == 4):
            logger.warning(f'failed to parse store id from {filename_td.text}')
            continue
        city = fix_city(city)
        href ,= anchor_td.xpath('./a/@href')
        hrefs.append((href, fix_address(address), city, store_id))


    if not hrefs:
        logger.warning(f'no prices found for boso')
        return []

    prod = []
    for url, address, city, store_id in hrefs:
        logger.debug(f'fetching prices for {boso.name} {store_id} ({address}, {city}) from {url}')
        if store_id not in boso.locations:
            boso.locations[store_id] = [city, None, address, None, None, None]

        rows = get_csv_rows(cached_fetch(url), delimiter=';', encoding='utf8')
        for k in rows[1:]:
            *name, _id, brand, _qty, units, mpc, ppu, discount_mpc, last_30d_mpc, may2_price, barcode, category = k
            barcode = barcode.lstrip('0')
            if not barcode:
                continue

            price = float(discount_mpc or mpc)
            may2_price = float('0' + may2_price) or None  # po defaultu je nula

            name = ' '.join(name).strip().replace('Æ', 'ć')
            while '  ' in name:
                name = name.replace('  ', ' ')

            resolve_product(prod, barcode, boso, store_id, name, price, None, may2_price)


    return prod