from datetime import datetime

from loguru import logger

from cijeneorg.fetchers.archiver import WaybackArchiver, Pricelist
from cijeneorg.fetchers.common import xpath, ensure_archived, get_csv_rows, resolve_product
from cijeneorg.models import Store


def fetch_rotodinamic_prices(rotodinamic: Store):
    WaybackArchiver.archive(index_url := 'https://www.rotodinamic.hr/cjenici/')
    coll = []
    for href in xpath(index_url, '//a[contains(@href, ".csv")]/@href'):
        filename = href.rsplit('/', 1)[-1]
        *_, date_str, time_str = href.rsplit(', ')
        dt = datetime.strptime(f'{date_str} {time_str}', '%d.%m.%Y %H.%M.csv')
        coll.append(Pricelist(href, '(sve poslovnice)', None, rotodinamic.id, None, dt, filename))

    if not coll:
        logger.warning('no rotodinamic prices found')
        return []

    logger.info(f'found {len(coll)} rotodinamic pricelists')
    coll.sort(key=lambda x: x.dt, reverse=True)
    today = coll[0].dt.date()
    today_coll = []
    for p in coll:
        if p.dt.date() == today:
            today_coll.append(p)
        else:
            ensure_archived(p)

    prod = []
    for p in today_coll:
        rows = get_csv_rows(ensure_archived(p, True))
        for k in rows[1:]:
            _id, name, category, brand, barcode, _qty, unit, mpc, ppu, discount_mpc, last_30d_mpc, may2_price = k
            # same pricelist for all those cash&carry locations
            for loc_id in 'D01 D28 D34 D18 D22 D13 D26 D11 D09'.split():
                resolve_product(prod, barcode, rotodinamic, loc_id, name, discount_mpc or mpc, _qty, may2_price)

    return prod