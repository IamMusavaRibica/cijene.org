from datetime import datetime
from urllib.parse import unquote

from loguru import logger

from cijenelib.fetchers._common import get_csv_rows, cached_fetch, resolve_product
from cijenelib.models import Store
import requests

from lxml.etree import HTML, tostring
from cijenelib.utils import UA_HEADER, fix_city


def fetch_trgovina_krk_prices(trgovina_krk: Store):
    # returns 403 forbidden if we don't use a user-agent. is this legal?
    root0 = HTML(requests.get('https://trgovina-krk.hr/objava-cjenika/', headers=UA_HEADER).content)
    hrefs = []
    for href in root0.xpath('//a[contains(@href, ".csv")]/@href'):
        filename = unquote(href).removeprefix('https://trgovina-krk.hr/csv/').removesuffix('.csv')
        *prefix, city, store_id, _id, datestr, h, m, s = filename.split('_')
        day, month, year = map(int, (datestr[:2], datestr[2:4], datestr[4:]))
        h, m, s = map(int, (h, m, s))
        dt = datetime(year, month, day, h, m, s)
        # print([prefix, city, store_id, dt])
        market_type = prefix[0]
        address = ' '.join(prefix[1:]).replace('  ', ' ').strip()
        city = fix_city(city)
        hrefs.append((dt, href, store_id, address, city))

    if not hrefs:
        logger.warning(f'no prices found for trgovina krk')
        return []
    prod = []
    hrefs.sort(reverse=True)
    today = hrefs[0][0].date()
    for d, url, store_id, address, city in hrefs:
        if d.date() != today:
            break
        if store_id not in trgovina_krk.locations:
            trgovina_krk.locations[store_id] = [city, None, address, None, None, None]
        logger.debug(f'fetching {url} for trgovina krk {store_id}, {address}, {city}')

        rows = get_csv_rows(cached_fetch(url), delimiter=';', encoding='cp1250')
        parsed_barcodes = set()
        for row in rows[1:]:
            try:
                name, _id, brand, _qty, units, mpc, ppu, discount_mpc, last_30d_mpc, may2_price, barcode, category = row
            except ValueError:
                logger.warning(f'{url}, {row}')
                continue
            # print([name, discount_mpc or mpc, barcode])
            if not barcode or barcode in parsed_barcodes:
                continue
            parsed_barcodes.add(barcode)

            name = name.removesuffix(' COCA-COLA').removesuffix(' COCA COLA').removesuffix(' COCA')
            price = float('0' + (discount_mpc or mpc).replace(',', '.'))
            may2_price = float('0' + may2_price.replace(',', '.')) or None
            resolve_product(prod, barcode, trgovina_krk, store_id, name, price, None, may2_price)


    return prod