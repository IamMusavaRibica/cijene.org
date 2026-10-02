import io
import zipfile
from datetime import datetime, date

from loguru import logger

from cijeneorg.fetchers.archiver import PriceList, WaybackArchiver
from cijeneorg.fetchers.common import get_csv_rows, resolve_product, xpath, ensure_archived, extract_offers_since
from cijeneorg.models import Store
from cijeneorg.utils import DDMMYYYY_dots, fix_city, DDMMYYYY_underscores_or_dots


def fetch_lidl_prices(lidl: Store, min_date: date):
    WaybackArchiver.archive(index_url := 'https://www.lidl.hr/c/cijene/s10073252')
    coll = []
    # TODO: a single request instead of two
    # /content/download up until 12.11.2025. /file/download after that
    for href in xpath(index_url, '//a[contains(@href, ".csv")]/@href'):
        href = str(href)
        if href.startswith('/'):
            href = 'https://www.lidl.hr' + href

        if m := DDMMYYYY_dots.findall(href):
            filename = href.rsplit('/', 1)[-1]
            try:
                day, month, year = map(int, *m)
                dt = datetime(year, month, day)
                location_type_and_id, rest = filename.split('_', maxsplit=1)
                location_id = location_type_and_id.split()[1]
                # for Address and City please take them from store_locations using location_id
                coll.append(PriceList(href, None, None, lidl.id, location_id, dt, filename))
            except Exception as e:
                logger.exception('cannot parse lidl filename `{}`', filename)
        else:
            logger.critical(f'failed to extract date from {p.text} !!')

    actual = extract_offers_since(lidl, coll, min_date, wayback=True, wayback_past=False)

    prod = []
    for p in actual:
        rows = get_csv_rows(ensure_archived(p, True, wayback=False))
        for k in rows[1:]:
            try:
                name, _id, _qty, units, brand, mpc, discount_mpc, last_30d_mpc, ppu, barcode, category, may2_price = k
            except ValueError:
                continue
            if not may2_price or 'Nije_bilo' in may2_price:
                may2_price = None
            resolve_product(prod, barcode, lidl, p.location_id, name, brand, discount_mpc or mpc, _qty, may2_price, p.date)

    return prod
