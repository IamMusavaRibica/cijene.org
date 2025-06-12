import concurrent.futures
from datetime import date, datetime

import requests
from loguru import logger

from cijeneorg.utils import ONE_DAY, fix_address, fix_city
from .archiver import WaybackArchiver, Pricelist
from .common import resolve_product, get_csv_rows, ensure_archived, extract_offers_from_today
from ..models import ProductOffer, Store

# https://www.spar.hr/usluge/cjenici
INDEX_URL = 'https://www.spar.hr/datoteke_cjenici/Cjenik{:%Y%m%d}.json'
MULTIPLE_WORD_CITIES = {'dugo_selo', 'donja_stubica', 'grubisno_polje', 'slavonski_brod', 'velika_gorica',
    'kastel_sucurac', 'marija_bistrica', 'novi_marof', 'sv._ivan_zelina', 'sesvetski_kraljevec', 'krapinske_toplice',
    'donji_stupnik', 'ivanic_grad', }

def fetch_spar_prices(spar: Store) -> list[ProductOffer]:
    WaybackArchiver.archive('https://www.spar.hr/datoteke_cjenici/index.html')
    d = date.today() + ONE_DAY
    yesterday = date.today() - ONE_DAY
    files = []
    while d.toordinal() > 739385:  # date(2025, 5, 14)
        url = INDEX_URL.format(d)
        if d >= yesterday:
            WaybackArchiver.archive(url)
        r = requests.get(url)
        if r.status_code == 200:
            try:
                files.extend(r.json()['files'])
            except Exception as e:
                logger.error(f'error parsing spar pricelist index at {url}: {e!r}')
        d -= ONE_DAY

    coll = []
    for f in files:
        filename = f['name']
        url = f['URL']
        market_type, *full_addr, _id, datestr, timestr = filename.removesuffix('.csv').split('_')
        num_city_words = 1
        for t in MULTIPLE_WORD_CITIES:
            if t in filename:
                num_city_words += t.count('_')
                break
        city, full_addr = full_addr[:num_city_words], full_addr[num_city_words:]
        city = fix_city(' '.join(city).replace('_', ' '))
        for j, el in enumerate(full_addr):
            if el.isdigit() and int(el) > 8000:
                location_id = el
                full_addr = full_addr[:j]
                break
        else:
            logger.warning(f'couldnt find location id in {filename}')
            continue

        if len(full_addr) >= 2 and full_addr[-1].isdigit() and full_addr[-2].isdigit():
            full_addr.append(full_addr.pop(-2) + '/' + full_addr.pop(-1))

        address = fix_address(' '.join(full_addr))
        dt = datetime.strptime(datestr + timestr, '%Y%m%d%H%M%S')
        coll.append(Pricelist(url, address, city, spar.id, location_id, dt, filename))

    today_coll = extract_offers_from_today(spar, coll)

    results = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=30, thread_name_prefix='Spar') as executor:
        futures = [executor.submit(fetch_single, p, spar) for p in today_coll]
        for fut in concurrent.futures.as_completed(futures):
            try:
                if res := fut.result():
                    results.extend(res)
            except Exception as e:
                logger.error(f'error fetching spar prices: {e!r}')
                continue

    return results


def fetch_single(p: Pricelist, spar: Store) -> list[ProductOffer]:
    rows = get_csv_rows(ensure_archived(p, True, wayback=False))
    prod = []
    for k in rows[1:]:
        name, _id, brand, _qty, unit, mpc, ppu, discount_mpc, last_30d_mpc, may2_price, barcode, category = k
        resolve_product(prod, barcode, spar, p.location_id, name, discount_mpc or mpc, _qty, may2_price)
    return prod