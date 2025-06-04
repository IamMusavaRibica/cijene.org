import io
import zipfile
from datetime import date

import requests
from loguru import logger
from lxml.etree import HTML, tostring

from cijenelib.fetchers._common import cached_fetch, get_csv_rows, resolve_product
from cijenelib.models import Store
from cijenelib.utils import DDMMYYYY_dots, fix_city


def fetch_eurospin_prices(eurospin: Store):
    root0 = HTML(requests.get('https://www.eurospin.hr/cjenik/').content)
    hrefs = []
    for option in root0.xpath('//option[contains(@value, "cjenik")]'):
        href = option.get('value')
        if m := DDMMYYYY_dots.findall(option.text.strip()):
            day, month, year = map(int, *m)
            dd = date(year, month, day)
            hrefs.append((dd, href))
        else:
            logger.warning(f'couldn\'t find date: {tostring(option)}')
            continue
    if not hrefs:
        logger.error('no valid download links found on the Eurospin prices page.')
        return []

    today, zip_url = max(hrefs)
    prod = []
    with zipfile.ZipFile(io.BytesIO(cached_fetch(zip_url))) as zf:
        for filename in zf.namelist():
            if not filename.endswith('.csv'):
                logger.warning(f'unexpected file in Eurospin zip: {filename}')
                continue

            market_type, store_id, *full_addr, city, postal_code, _id, _date, _ = filename.split('-')
            city = fix_city(city.replace('_', ' '))
            address = ' '.join(full_addr).replace('_', ' ')
            if store_id not in eurospin.locations:
                eurospin.locations[store_id] = [city, None, address, None, None, None]

            with zf.open(filename) as f:
                rows = get_csv_rows(f.read(), delimiter=';', encoding='cp1250')
                for k in rows[1:]:
                    name, _id, brand, _qty, units, mpc, ppu, discount_mpc, _, last_30d_mpc, may2_price, barcode, category = k
                    if not barcode:
                        continue
                    quantity = float(_qty.replace(',', '.'))
                    price = float((discount_mpc or mpc).replace(',', '.'))
                    may2_price = float(may2_price.replace(',', '.')) if may2_price else None

                    resolve_product(prod, barcode, eurospin, store_id, name.strip(), price, quantity, may2_price)

    return prod