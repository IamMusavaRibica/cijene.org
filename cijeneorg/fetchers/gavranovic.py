import re
from datetime import datetime, date
from urllib.parse import unquote

from loguru import logger

from cijeneorg.fetchers.archiver import PriceList, WaybackArchiver
from cijeneorg.fetchers.common import get_csv_rows, resolve_product, xpath, ensure_archived, extract_offers_since
from cijeneorg.models import Store
from cijeneorg.utils import fix_address, fix_city


def fetch_gavranovic_prices(gavranovic: Store, min_date: date):
    WaybackArchiver.archive(BASE_URL := 'https://gavranoviccjenik.com.hr/')
    coll = []
    for href in xpath(BASE_URL, '//a[contains(@href, ".csv")]/@href'):
        full_url = BASE_URL + href.removeprefix('/')
        filename = unquote(href)
        if not filename.endswith('.csv'):
            logger.warning(f'unexpected file in gavranovic pricelist: {filename}')
            continue

        # ddmmyyyy_HH_MM_SS
        if m := re.search(r'([0123]\d)([01]\d)(20\d\d)_([012]\d)_(\d\d)_(\d\d)', filename):
            dd, mm, yyyy, HH, MM, SS = map(int, m.groups())
            dt = datetime(yyyy, mm, dd, HH, MM, SS)
            _segments = filename[:m.start()-1].split('_')[1:]  # remove Supermarket as first word
            file_id = _segments.pop()
            location_id = _segments.pop()
            city = _segments.pop()
            address = ' '.join(_segments)
            coll.append(PriceList(full_url, fix_address(address), fix_city(city), gavranovic.id, location_id, dt, filename))
        else:
            logger.warning(f'failed to extract data from {filename}')
            continue

    actual = extract_offers_since(gavranovic, coll, min_date)

    prod = []
    for p in actual:
        rows = get_csv_rows(ensure_archived(p, True, wayback=False))
        for k in rows[1:]:
            name, _id, brand, _qty, units, mpc, ppu, discount_mpc, last_30d_mpc, may2_price, barcode, category = k
            resolve_product(prod, barcode, gavranovic, p.location_id, name, brand, discount_mpc or mpc, _qty, may2_price, p.date)

    return prod
