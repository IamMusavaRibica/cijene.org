import concurrent.futures
import re
import time
from datetime import datetime

import requests
from loguru import logger
from lxml.etree import HTML

from cijeneorg.models import Store
from cijeneorg.utils import fix_address, DDMMYYYY_dots, fix_city
from .archiver import PriceList, WaybackArchiver
from .common import get_csv_rows, resolve_product, ensure_archived, extract_offers_from_today


def fetch_konzum_prices(konzum: Store):
    WaybackArchiver.archive(index_url := 'https://www.konzum.hr/cjenici/')

    root0 = HTML(requests.get(index_url).content)
    max_page = 0
    available_dates_urls = []
    for page in root0.xpath('//a[starts-with(@href, "/cjenici?page=")]'):
        if page.text.isnumeric():
            max_page = max(max_page, int(page.text))
    for date in root0.xpath('//a[starts-with(@href, "/cjenici?date=")]/@href'):
        available_dates_urls.append(date.removeprefix('/cjenici?date='))

    # fetch every page
    _start = time.perf_counter()
    pages = [root0]
    with concurrent.futures.ThreadPoolExecutor(max_workers=16, thread_name_prefix='Konzum_Pages') as executor:
        futures = []
        for d in available_dates_urls:
            for i in range(2, max_page + 1):
                page_url = f'{index_url}?date={d}&page={i}'
                WaybackArchiver.archive(page_url)
                futures.append(executor.submit(lambda _url: HTML(requests.get(_url).content), page_url))

        for future in concurrent.futures.as_completed(futures):
            pages.append(future.result())

    logger.info(f'fetched {len(pages)} konzum pages, took {time.perf_counter() - _start:.3f} s')

    # extract all pricelists from the pages
    coll = []
    for root in pages:
        for a in root.xpath('//h5/a[starts-with(@href, "/cjenici/download")]'):
            url = 'https://www.konzum.hr' + a.get('href')

            s = a.text.strip()
            if s[-18:-4].isnumeric():  # SUPERMARKET,adresa,0901,465,20250516081939.CSV
                store_type, *full_addr, location_id, file_id, datestr = s.split(',')
                dt = datetime.strptime(datestr.lower(), '%Y%m%d%H%M%S.csv')
            else:
                store_type, *full_addr, location_id, file_id, date, _ = a.text.strip().split(',')
                if not (m := DDMMYYYY_dots.match(date)):
                    logger.warning(f'unexpected date format (failed to parse?) {a.text.strip()}')
                    continue
                day, month, year = map(int, m.groups())
                dt = datetime(year, month, day)

            if not (len(location_id) == 4 and location_id.isnumeric()):
                logger.warning(f'unexpected location id (failed to parse?) {a.text.strip()}')
                continue

            full_addr = ' '.join(full_addr).replace(',', ' ').replace('_', ' ')
            # parse the address to extract street and city
            five_digit_nums = list(re.finditer(r'\b\d{5}\b', full_addr))
            if not five_digit_nums:
                logger.warning(f'unexpected address format (failed to parse?) {a.text.strip()}')
                continue

            postal_match = five_digit_nums[-1]
            address = full_addr[:postal_match.start()].strip()
            postal_code = postal_match.group(0)

            city = fix_city(full_addr[postal_match.end():])
            address = fix_address(address)
            coll.append(PriceList(url, address, city, konzum.id, location_id, dt, a.text.strip()))

    today_coll = extract_offers_from_today(konzum, coll)

    all_products = []
    # TODO: different threads will access the sqlite database, is it safe?
    with concurrent.futures.ThreadPoolExecutor(max_workers=32, thread_name_prefix='Konzum') as executor:
        futures = []
        for p in today_coll:
            futures.append(executor.submit(process_single, konzum, p))

        for future in concurrent.futures.as_completed(futures):
            try:
                all_products.extend(future.result())
            except Exception as e:
                logger.error(f'error processing a price list')
                logger.exception(e)

    return all_products

def process_single(konzum: Store, p: PriceList):
    rows = get_csv_rows(ensure_archived(p, True, wayback=False))
    coll = []
    for k in rows[1:]:
        # za konzum, unit == 'ko' za pakirane proizvode, 'kg' za proizvode u rinfuzi
        name, _id, brand, total_qty, _, mpc, ppu, discount_mpc, last_30d_mpc, may2_price, barcode, category = k
        quantity, unit = total_qty.split()
        resolve_product(coll, barcode, konzum, p.location_id, name, discount_mpc or mpc, quantity, may2_price)
    return coll