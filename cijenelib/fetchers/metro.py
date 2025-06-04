from loguru import logger

from cijenelib.fetchers._common import get_csv_rows, cached_fetch, resolve_product
from cijenelib.models import Store
import requests
import re
from lxml.etree import HTML
from datetime import date
from urllib.parse import unquote

from cijenelib.utils import fix_address, fix_city

BASE_URL = 'https://metrocjenik.com.hr/'
def fetch_metro_prices(metro: Store):
    root0 = HTML(requests.get(BASE_URL).content)
    hrefs = []
    for href in root0.xpath('//a[contains(@href, ".csv")]/@href'):
        if yyyymmdd := list(re.finditer(r'(20\d{2})([01]\d)([0123]\d)', href)):
            m = yyyymmdd[0]
            year, month, day = map(int, m.groups())
            dd = date(year, month, day)
            store_id, rest = href[m.end() + 6:].split('_', 1)
            address, city = unquote(rest).replace('_', ' ').removesuffix('.csv').split(',')
            city = fix_city(city.strip().title())
            address = fix_address(address)
            hrefs.append((dd, BASE_URL+href, store_id, address, city))

    if not hrefs:
        logger.warning(f'no valid metro pricelists found!')
        return []

    hrefs.sort(reverse=True)
    today = hrefs[0][0]
    prod = []
    for _date, url, store_id, address, city in hrefs:
        if _date != today:
            break

        if store_id not in metro.locations:
            metro.locations[store_id] = [city, None, address, None, None, None]

        logger.debug(f'fetching metro prices for {store_id} {address}, {city}')
        rows = get_csv_rows(cached_fetch(url), delimiter=',', encoding='utf-8')
        for k in rows[1:]:
            name, _id, brand, _qty, units, mpc, ppu, discount_mpc, last_30d_mpc, may2_price, barcode, category = k
            if not barcode:
                continue
            price = float('0' + (discount_mpc or mpc))
            may2_price = float('0' + may2_price) if may2_price else None
            resolve_product(prod, barcode, metro, store_id, name, price, None, may2_price)

    return prod