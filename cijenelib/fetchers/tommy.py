import concurrent.futures
from datetime import date, datetime

import requests
from loguru import logger

from cijenelib.fetchers._archiver import WaybackArchiver, Pricelist
from cijenelib.fetchers._common import get_csv_rows, resolve_product, ensure_archived
from cijenelib.models import Store
from cijenelib.utils import ONE_DAY, fix_address, fix_city

BASE_URL = 'https://spiza.tommy.hr'
API_URL = 'https://spiza.tommy.hr/api/v2/shop/store-prices-tables?itemsPerPage=789&date={:%Y-%m-%d}'
def fetch_tommy_prices(tommy: Store):
    WaybackArchiver.archive('https://www.tommy.hr/objava-cjenika')
    d = date.today() + ONE_DAY
    files = []
    while d.toordinal() > 739385:  # date(2025, 5, 14)
        WaybackArchiver.archive(url := API_URL.format(d))
        r = requests.get(url)
        logger.debug(f'fetching Tommy pricelist index at {url} - status: {r.status_code}')
        if r.status_code == 200:
            try:
                files.extend(r.json()['hydra:member'])
            except Exception as e:
                logger.error(f'error parsing tommy pricelist index at {url}: {e!r}')
        d -= ONE_DAY

    coll = []
    for f in files:
        filename = f['fileName']
        url = BASE_URL + f['@id']
        # 'SUPERMARKET, ANTE STARČEVIĆA 114, 21300 MAKARSKA, 10152, 27, 20250606 0530'
        market_type, address, city, location_id, file_id, dt_str = filename.split(', ')
        if city[:5].isdigit():  # remove postal code
            city = city[5:].strip()
        city = fix_city(city)
        address = fix_address(address)
        if not (location_id.isdigit() and len(location_id) == 5):
            logger.warning(f'failed to parse tommy filename {filename}')
            continue
        dt = datetime.strptime(dt_str, '%Y%m%d %H%M')
        coll.append(Pricelist(url, address, city, tommy.id, location_id, dt, filename))

    if not coll:
        logger.warning('no tommy pricelists found')
        return []

    logger.info(f'found {len(coll)} tommy pricelists')
    coll.sort(key=lambda x: x.dt, reverse=True)
    today = coll[0].dt.date()
    today_coll = []
    for p in coll:
        if p.dt.date() == today:
            today_coll.append(p)
        else:
            ensure_archived(p)

    prod = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=12, thread_name_prefix='Tommy') as executor:
        futures = [executor.submit(fetch_single, p, tommy) for p in today_coll]
        for future in concurrent.futures.as_completed(futures):
            try:
                prod.extend(future.result())
            except Exception as e:
                logger.error(f'error fetching or parsing Tommy prices {e!r}')
                continue

    return prod


def fetch_single(p: Pricelist, tommy: Store):
    rows = get_csv_rows(ensure_archived(p, True))

    coll = []
    for k in rows[1:]:
        # last two are: DATUM_ULASKA_NOVOG_ARTIKLA, PRVA_CIJENA_NOVOG_ARTIKLA
        barcode, _id, name, brand, category, unit, _qty, mpc, discount_mpc, ppu, last_30d_mpc, may2_price, _, _ = k
        resolve_product(coll, barcode, tommy, p.location_id, name, discount_mpc or mpc, _qty, may2_price)
    return coll