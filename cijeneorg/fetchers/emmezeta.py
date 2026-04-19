from datetime import datetime, date

from loguru import logger

from cijeneorg.fetchers.archiver import PriceList, WaybackArchiver
from cijeneorg.fetchers.common import get_csv_rows, resolve_product, xpath, ensure_archived, extract_offers_since
from cijeneorg.models import Store


def fetch_emmezeta_prices(emmezeta: Store, min_date: date):
    WaybackArchiver.archive(BASE_URL := 'https://s3.emmezeta.hr/csv/csv_list.html')
    coll = []
    for full_url in xpath(BASE_URL, '//a[contains(@href, ".csv")]/@href'):
        filename = full_url.rsplit('/', 1)[-1]
        try:
            date_str = (filename.removeprefix('Emmezeta_')
                        .removesuffix('.csv')
                        .replace('.', '')
                        [:8])
            dd = int(date_str[:2])
            mm = int(date_str[2:4])
            yyyy = int(date_str[4:8])
            dt = datetime(yyyy, mm, dd)
            coll.append(PriceList(full_url, '???', '???', emmezeta.id, '(sve trgovine)', dt, filename))
        except:
            logger.exception(f'failed to parse filename {filename} for emmezeta')
            continue

    actual = extract_offers_since(emmezeta, coll, min_date)

    prod = []
    for p in actual:
        rows = get_csv_rows(ensure_archived(p, True, wayback=False))
        for k in rows[1:]:
            name, _id, brand, category, units, _qty, mpc, _mass, _3d, _h, _w, barcode, last_30d_mpc, may2_price = k
            resolve_product(prod, barcode, emmezeta, p.location_id, name, brand, mpc, _qty, may2_price, p.date)

    return prod
