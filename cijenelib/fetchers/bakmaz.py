from datetime import datetime

from loguru import logger

from cijenelib.fetchers._archiver import Pricelist
from cijenelib.fetchers._common import xpath, ensure_archived, get_csv_rows, resolve_product
from cijenelib.models import Store
from cijenelib.utils import fix_city


def fetch_bakmaz_prices(bakmaz: Store):
    coll = []
    for url in xpath('https://www.bakmaz.hr/o-nama/', '//a[@class="btn-preuzmi"]/@href'):

        filename = url.rsplit('/', 1)[-1]
        if not filename.endswith('.csv'):
            logger.warning(f'unexpected non-csv href: {url}')
            continue
        try:
            market_type, address, city, location_id, file_id, dtstr = filename.split('_', 5)
            address = address.replace('-', ' ')
            city = fix_city(city)
            dt = datetime.strptime(dtstr.replace('_', ''), '%d%m%Y%H%M%S.csv')
            coll.append(Pricelist(url, address, city, bakmaz.id, location_id, dt, filename))
        except Exception as e:
            logger.warning(f'error {e!r} while bakmaz pricelist {filename = }')
            logger.exception(e)
            continue

    if not coll:
        logger.warning('no bakmaz prices found')
        return []

    logger.info(f'found {len(coll)} bakmaz prices')
    coll.sort(key=lambda x: x.dt, reverse=True)
    today = coll[0].dt.date()
    today_coll = []
    for p in coll:
        if p.dt.date() == today:
            today_coll.append(p)
        else:
            ensure_archived(p)

    prod = []
    for t in today_coll:
        rows = get_csv_rows(ensure_archived(t, True))
        for k in rows[1:]:
            name, _id, brand, _qty, units, mpc, ppu, discount_mpc, last_30d_mpc, may2_price, barcode, category = k
            resolve_product(prod, barcode, bakmaz, t.location_id, name, discount_mpc or mpc, _qty, may2_price)

    return prod