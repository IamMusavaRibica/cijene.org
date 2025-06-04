import io
import zipfile
from datetime import date

import requests
from loguru import logger
from lxml.etree import HTML, tostring

from cijenelib.fetchers._common import cached_fetch, get_csv_rows, resolve_product
from cijenelib.models import Store
from cijenelib.utils import DDMMYYYY_dots, fix_city


def fetch_lidl_prices(lidl: Store):
    root0 = HTML(requests.get('https://tvrtka.lidl.hr/cijene').content)
    hrefs: list[tuple[date, str]] = []
    for p in root0.xpath('//a[starts-with(@href, "https://tvrtka.lidl.hr/content/download/")]/..'):
        if m := DDMMYYYY_dots.findall(p.text):
            day, month, year = map(int, *m)
            dd = date(year, month, day)
            href ,= p.xpath('a/@href')
            hrefs.append((dd, href))
        else:
            logger.warning(f'couldn\'t find date: {tostring(p)}')

    _, zip_url = max(hrefs)
    zip_data = cached_fetch(zip_url)

    prod = []
    with zipfile.ZipFile(io.BytesIO(zip_data)) as zf:
        for filename in zf.namelist():
            if not filename.endswith('.csv'):
                logger.warning(f'unexpected file in lidl zip: {filename}')
                continue

            market, *address, postal_code, city, id0, _date, _ = filename.split('_')
            store_type, store_id = market.split()
            city = fix_city(city)
            if store_id not in lidl.locations:
                lidl.locations[store_id] = [city, None, ' '.join(address), None, None, None]

            with zf.open(filename) as file:
                rows = get_csv_rows(file.read(), delimiter=',', encoding='cp1250')
                for k in rows[1:]:
                    # index 3: neto kolicina, but it is weird
                    name, _id, net_qty, _, brand, mpc, discount_mpc, last_30d_mpc, ppu, barcode, category, may2_price = k
                    if not barcode:
                        continue

                    quantity = float(net_qty)
                    price = mpc or discount_mpc
                    if not price:
                        logger.warning(f'product {name}, {barcode =} has no price')
                        continue
                    price = float(price)
                    may2_price = float(may2_price.replace(',', '.')) \
                                if may2_price and 'Nije_bilo' not in may2_price else None

                    resolve_product(prod, barcode, lidl, store_id, name, price, quantity, may2_price)
    return prod