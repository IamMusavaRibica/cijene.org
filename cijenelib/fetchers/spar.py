import concurrent.futures
import csv
import io

from loguru import logger

from ._common import cached_fetch, resolve_product, get_csv_rows
from ..models import ProductOffer, Store
from datetime import date
from cijenelib.utils import ONE_DAY, fix_address, fix_city
import requests


# https://www.spar.hr/usluge/cjenici
INDEX_URL = 'https://www.spar.hr/datoteke_cjenici/Cjenik{:%Y%m%d}.json'
def fetch_spar_prices(spar: Store) -> list[ProductOffer]:
    d = date.today() + ONE_DAY
    index = None
    for _ in range(3):
        r = requests.get(INDEX_URL.format(d))
        if r.status_code == 200:
            index = r.json()['files']
            break
        d -= ONE_DAY

    if not index:
        logger.warning('could not find Spar price lists')
        return []

    hrefs = []
    for i in index:
        filename = i['name']
        url = i['URL']
        market_type, *full_addr, _id, datestr, timestr = filename.removesuffix('.csv').split('_')
        num_city_words = 1
        for t in {'dugo_selo', 'donja_stubica', 'grubisno_polje', 'slavonski_brod', 'velika_gorica', 'kastel_sucurac',
                  'marija_bistrica', 'novi_marof', 'sv._ivan_zelina', 'sesvetski_kraljevec', 'krapinske_toplice',
                  'donji_stupnik', 'ivanic_grad'}:
            if t in filename:
                num_city_words += t.count('_')
                break
        city, full_addr = full_addr[:num_city_words], full_addr[num_city_words:]
        city = ' '.join(city).replace('_', ' ').title()
        city = fix_city(city)
        for j, el in enumerate(full_addr):
            if el.isdigit() and int(el) > 8000:
                store_id = el
                full_addr = full_addr[:j]
                break
        else:
            logger.warning(f'couldnt find store id in {filename}')
            continue
        if len(full_addr) >= 2 and full_addr[-1].isdigit() and full_addr[-2].isdigit():
            full_addr.append(full_addr.pop(-2) + '/' + full_addr.pop(-1))
        address = fix_address(' '.join(full_addr))

        if store_id not in spar.locations:
            spar.locations[store_id] = [city, None, address, None, None, None]

        hrefs.append((url, store_id))

    results = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=30, thread_name_prefix='Spar') as executor:
        futures = [executor.submit(fetch_single, spar, url, store_id) for url, store_id in hrefs]
        for fut in concurrent.futures.as_completed(futures):
            try:
                if res := fut.result():
                    results.extend(res)
            except Exception as e:
                logger.error(f'Error fetching Spar prices: {e}')
                continue

    return results






def fetch_single(spar: Store, url: str, store_id: str) -> list[ProductOffer]:
    rows = get_csv_rows(cached_fetch(url), delimiter=';', encoding='cp1250')
    prod = []
    for k in rows[1:]:
        name, _id, brand, total_qty, unit, mpc, ppu, discount_mpc, last_30d_mpc, may2_price, barcode, category = k

        if not barcode:
            continue

        quantity = float(total_qty.replace(',', '.'))
        if not (price := mpc or discount_mpc):
            # logger.warning(f'[Spar] store {store_id} product {name}, barcode {barcode} has no current price')
            continue
        price = float(price.replace(',', '.'))
        may2_price = float(may2_price.replace(',', '.')) if may2_price else None
        resolve_product(prod, barcode, spar, store_id, name, price, quantity, may2_price)

    return prod