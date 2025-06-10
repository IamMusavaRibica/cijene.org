import re
from datetime import datetime, date

from loguru import logger

from cijenelib.fetchers._archiver import Pricelist, WaybackArchiver
from cijenelib.fetchers._common import get_csv_rows, resolve_product, xpath, ensure_archived
from cijenelib.models import Store
from cijenelib.utils import fix_address, fix_city, ONE_DAY


def fetch_ktc_prices(ktc: Store):
    # https://www.ktc.hr/cjenici
    HOST = 'https://www.ktc.hr/'
    WaybackArchiver.archive(index_url := HOST + 'cjenici')
    coll = []
    yesterday = date.today() - ONE_DAY
    for href0 in xpath(index_url, '//a[contains(@href, "cjenici?poslovnica")]/@href'):
        location_id = (m := re.search(r'PJ-\w+', href0)) and m.group()
        if location_id is None:
            logger.warning(f'failed to extract location id from {href0}')
            continue
        for href1 in xpath(HOST + href0.removeprefix('/'), '//a[contains(@href, ".csv")]/@href'):
            full_url = HOST + href1.removeprefix('/')
            filename = href1.rsplit('/', 1)[-1]
            market_type, _addr_city, _, file_id, datestr = filename.split('-', 4)
            dt = datetime.strptime(datestr, '%Y%m%d-%H%M%S.csv')

            if dt >= yesterday:
                WaybackArchiver.archive(full_url)

            # cities with two word names
            for t in {'GRUBISNO POLJE', 'MURSKO SREDISCE', 'VELIKA GORICA', 'DUGO SELO'}:
                if _addr_city.endswith(t):
                    addr = _addr_city[:-len(t)]
                    city = t
                    break
            else:
                *a, city = _addr_city.rsplit(maxsplit=1)
                addr = ' '.join(a)
            addr = fix_address(addr)
            city = fix_city(city)
            coll.append(Pricelist(full_url, addr, city, ktc.id, location_id, dt, filename))

    if not coll:
        logger.warning('no KTC pricelists found')
        return []

    logger.info(f'found {len(coll)} ktc prices')
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
            # KTC does not have 2.5.2025. price
            name, _id, brand, _qty, units, mpc, ppu, barcode, category, last_30d_mpc, discount_mpc = k
            barcode = barcode.strip("'")
            price = float(discount_mpc) or float(mpc)
            resolve_product(prod, barcode, ktc, p.location_id, name, price, _qty, None)
    return prod