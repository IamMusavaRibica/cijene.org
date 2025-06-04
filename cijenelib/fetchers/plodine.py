import io
import re
import zipfile
from datetime import date

import requests
from loguru import logger
from lxml.etree import HTML, tostring

from cijenelib.fetchers._common import cached_fetch, get_csv_rows, resolve_product
from cijenelib.models import Store
from cijenelib.utils import DDMMYYYY_dots, fix_address, fix_city


def fetch_plodine_prices(plodine: Store):
    root0 = HTML(requests.get('https://www.plodine.hr/info-o-cijenama').content)
    hrefs = []
    for a in root0.xpath('//a[contains(@href, "plodine.hr/cjenici/")]'):
        href = a.get('href')
        if m := DDMMYYYY_dots.findall(a.text.strip()):
            day, month, year = map(int, *m)
            dd = date(year, month, day)
            hrefs.append((dd, href))
        else:
            logger.warning(f'couldn\'t find date: {a.text.strip()}')
    if not hrefs:
        logger.error('no valid download links found on the Plodine prices page.')
        return []
    _, zip_url = max(hrefs)

    zip_data = cached_fetch(zip_url)
    prod = []
    with zipfile.ZipFile(io.BytesIO(zip_data)) as zf:
        for filename in zf.namelist():
            if not filename.endswith('.csv'):
                logger.warning(f'unexpected file in Plodine zip: {filename}')
                continue

            market_type, *full_addr, store_id, _id, _ = filename.split('_')

            full_addr = ' '.join(full_addr)
            five_digit_nums = list(re.finditer(r'\b\d{5}\b', full_addr))
            if not five_digit_nums:
                logger.warning(f'unexpected address format (failed to parse?) {a.text.strip()}')
                continue

            postal_match = five_digit_nums[-1]
            address = full_addr[:postal_match.start()].strip()
            postal_code = postal_match.group(0)
            city = full_addr[postal_match.end():].strip().title()
            city = fix_city(city)
            address = fix_address(address)

            if store_id not in plodine.locations:
                plodine.locations[store_id] = [city, None, address, None, None, None]


            with zf.open(filename) as f:
                rows = get_csv_rows(f.read(), delimiter=';', encoding='utf8')
                for k in rows[1:]:
                    name, _id, brand, _qty, units, mpc, ppu, discount_mpc, last_30d_mpc, may2_price, barcode, category, *_ = k
                    if not barcode:
                        continue
                    if not _qty:
                        continue
                    quantity = float(_qty.split()[0].replace(',', '.'))
                    price = mpc or discount_mpc
                    if not price:
                        logger.warning(f'product {name}, {barcode =} has no price')
                        continue

                    # adding zeroes to the left will not cause any problems, right?
                    price = float('0' + price.replace(',', '.'))
                    may2_price = float('0' + may2_price.replace(',', '.')) \
                                 if may2_price else None

                    resolve_product(prod, barcode, plodine, store_id, name, price, quantity, may2_price)




    return prod