import re
from datetime import datetime
from urllib.parse import unquote

from loguru import logger

from cijeneorg.fetchers.archiver import Pricelist, WaybackArchiver
from cijeneorg.fetchers.common import get_csv_rows, resolve_product, xpath, ensure_archived
from cijeneorg.models import Store
from cijeneorg.utils import fix_address, fix_city


def fetch_metro_prices(metro: Store):
    WaybackArchiver.archive(BASE_URL := 'https://metrocjenik.com.hr/')
    coll = []
    for href in xpath(BASE_URL, '//a[contains(@href, ".csv")]/@href'):
        full_url = BASE_URL + href.removeprefix('/')
        filename = unquote(href)
        if not filename.endswith('.csv'):
            logger.warning(f'unexpected file in metro pricelist: {filename}')
            continue

        if m := re.search(r'(20\d\d)([01]\d)([0123]\d)T([012]\d)(\d\d)_', filename):
            dt = datetime(*map(int, m.groups()))
            location_id, _addr_city = filename[m.end():-4].split('_', 1)
            address, city = _addr_city.replace('_', ' ').rsplit(',', 1)
            coll.append(Pricelist(full_url, fix_address(address), fix_city(city), metro.id, location_id, dt, filename))
        else:
            logger.warning(f'failed to extract data from {filename}')
            continue

    if not coll:
        logger.warning(f'no metro pricelists found')
        return []

    logger.info(f'found {len(coll)} metro pricelists')
    coll.sort(key=lambda x: x.dt, reverse=True)
    today = coll[0].dt.date()
    today_coll = []
    for p in coll:
        if p.dt.date() == today:
            today_coll.append(p)
        else:
            ensure_archived(p, wayback=False)

    prod = []
    for p in today_coll:
        rows = get_csv_rows(ensure_archived(p, True, wayback=False))
        for k in rows[1:]:
            name, _id, brand, _qty, units, mpc, ppu, discount_mpc, last_30d_mpc, may2_price, barcode, category = k
            resolve_product(prod, barcode, metro, p.location_id, name, discount_mpc or mpc, _qty, may2_price)

    return prod