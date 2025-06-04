import concurrent.futures
import re

import requests
from loguru import logger
from lxml.etree import HTML

from cijenelib.models import Store
from cijenelib.utils import fix_address, DDMMYYYY_dots, fix_city
from ._common import cached_fetch, get_csv_rows, resolve_product


def fetch_konzum_prices(konzum: Store):
    index_url = 'https://www.konzum.hr/cjenici/'

    root0 = HTML(requests.get(index_url).content)
    max_page = 0
    for page in root0.xpath('//a[starts-with(@href, "/cjenici?page=")]'):
        if page.text.isnumeric():
            max_page = max(max_page, int(page.text))

    # fetch every page
    pages = [root0]
    for i in range(2, max_page+1):
        pages.append(HTML(requests.get(f'{index_url}?page={i}').content))

    # extract all pricelists from the pages
    hrefs: list[tuple[str, str]] = []
    for root in pages:
        for a in root.xpath('//h5/a[starts-with(@href, "/cjenici/download")]'):
            href = 'https://www.konzum.hr' + a.get('href')

            store_type, *full_addr, location_id, broj_pohrane, date, _ = a.text.strip().split(',')
            hrefs.append((href, location_id))
            # print([store_type, full_addr, location_id, broj_pohrane, date])

            if not (len(location_id) == 4 and location_id.isnumeric()):
                logger.warning(f'unexpected location id (failed to parse?) {a.text.strip()}')
                continue
            if not (m := DDMMYYYY_dots.match(date)):
                logger.warning(f'unexpected date format (failed to parse?) {a.text.strip()}')
                continue
            day, month, year = m.groups()

            # parse the address to extract street and city
            full_addr = ' '.join(full_addr)
            five_digit_nums = list(re.finditer(r'\b\d{5}\b', full_addr))
            if not five_digit_nums:
                logger.warning(f'unexpected address format (failed to parse?) {a.text.strip()}')
                continue

            postal_match = five_digit_nums[-1]
            address = full_addr[:postal_match.start()].strip()
            postal_code = postal_match.group(0)
            city = fix_city(full_addr[postal_match.end():])

            address = fix_address(address)

            if location_id not in konzum.locations:
                konzum.locations[location_id] = [city, None, address, None, None, None]

    logger.debug(f'found {len(hrefs)} price lists for konzum')
    all_products = []

    with concurrent.futures.ThreadPoolExecutor(max_workers=32, thread_name_prefix='Konzum') as executor:
        futures = []
        for href, location_id in hrefs:
            futures.append(executor.submit(process_single, href, konzum, location_id))

        for future in concurrent.futures.as_completed(futures):
            try:
                all_products.extend(future.result())
            except Exception as e:
                logger.error(f'error processing a price list')
                logger.exception(e)

    return all_products

def process_single(full_url: str, konzum: Store, location_id: str):
    logger.debug(f'processing store {location_id} from {full_url}')
    raw = cached_fetch(full_url)
    rows = get_csv_rows(raw, delimiter=',', encoding='utf8')
    coll = []
    for k in rows[1:]:
        # za konzum, unit == 'ko' za pakirane proizvode, 'kg' za proizvode u rinfuzi
        name, _id, brand, total_qty, _, mpc, ppu, discount_mpc, last_30d_mpc, may2_price, barcode, category = k
        if not barcode:
            continue
        quantity, unit = total_qty.split()
        quantity = float(quantity)
        price = mpc or discount_mpc
        if not price:
            logger.warning(f'product {name}, barcode {barcode} has no current price')
            continue
        price = float(price)
        may2_price = float(may2_price) if may2_price else None

        resolve_product(coll, barcode, konzum, location_id, name, price, quantity, may2_price)

    return coll