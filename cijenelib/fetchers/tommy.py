import concurrent.futures
import json

from cijenelib.fetchers._common import cached_fetch, get_csv_rows, resolve_product
from cijenelib.models import Store

from loguru import logger
import requests

from datetime import date

from cijenelib.utils import ONE_DAY, fix_address, fix_city

BASE_URL = 'https://spiza.tommy.hr'
API_URL = 'https://spiza.tommy.hr/api/v2/shop/store-prices-tables?itemsPerPage=789&date={:%Y-%m-%d}'
def fetch_tommy_prices(tommy: Store):
    d = date.today() + ONE_DAY
    for _ in range(3):
        if index := requests.get(API_URL.format(d)).json().get('hydra:member', []):
            break
        d -= ONE_DAY
    else:
        logger.warning(f'could not find Tommy pricelist')
        return []

    prod = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=30, thread_name_prefix='Tommy') as executor:
        futures = []
        for i in index:
            market_type, address, city, store_id, _id, *rest = i['fileName'].split(', ')
            address = fix_address(address)
            if city[:5].isdigit():  # remove postal code
                city = city[5:].strip()
            city = fix_city(city)
            if not (store_id.isdigit() and len(store_id) == 5):
                logger.warning(f'invalid store_id (failed to parse?) {i["fileName"]}')

            if store_id not in tommy.locations:
                tommy.locations[store_id] = [city, None, address, None, None, None]

            futures.append(executor.submit(fetch_single, BASE_URL + i['@id'], tommy, store_id))

        for future in concurrent.futures.as_completed(futures):
            try:
                coll = future.result()
            except Exception as e:
                logger.error(f'error fetching Tommy prices for {store_id}:')
                logger.exception(e)
                continue
            prod.extend(coll)
    return prod


def fetch_single(url, tommy, store_id):
    logger.debug(f'fetching Tommy prices for {store_id} at {url}')
    raw = cached_fetch(url)
    rows = get_csv_rows(raw, delimiter=',', encoding='utf8')

    coll = []
    for k in rows[1:]:
        # last two are: DATUM_ULASKA_NOVOG_ARTIKLA, PRVA_CIJENA_NOVOG_ARTIKLA
        barcode, _id, name, brand, category, unit, total_qty, mpc, discount_mpc, ppu, last_30d_mpc, may2_price, _, _ = k
        if not barcode:
            continue
        quantity = float(total_qty.replace(',', '.'))
        price = mpc or discount_mpc
        if not price:
            logger.warning(f'product {name}, barcode {barcode} has no current price')
            continue
        price = float(mpc.replace(',', '.')) if mpc else float(discount_mpc.replace(',', '.'))
        may2_price = float(may2_price.replace(',', '.')) if may2_price else None

        resolve_product(coll, barcode, tommy, store_id, name, price, quantity, may2_price)
    return coll