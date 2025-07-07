from datetime import datetime

from loguru import logger

from cijeneorg.fetchers.archiver import WaybackArchiver, PriceList
from cijeneorg.fetchers.common import xpath, ensure_archived, get_csv_rows, resolve_product, extract_offers_from_today
from cijeneorg.models import Store


def fetch_rotodinamic_prices(rotodinamic: Store):
    WaybackArchiver.archive(index_url := 'https://www.rotodinamic.hr/cjenici/')
    coll = []
    for href in xpath(index_url, '//a[contains(@href, ".csv")]/@href'):
        filename = href.rsplit('/', 1)[-1]
        *_, date_str, time_str = href.rsplit(', ')
        dt = datetime.strptime(f'{date_str} {time_str}', '%d.%m.%Y %H.%M.csv')
        coll.append(PriceList(href, '(sve poslovnice)', None, rotodinamic.id, None, dt, filename))

    today_coll = extract_offers_from_today(rotodinamic, coll, wayback=True)

    prod = []
    for p in today_coll:
        rows = get_csv_rows(ensure_archived(p, True))
        for k in rows[1:]:
            try:
                _id, name, category, brand, barcode, _qty, unit, mpc, ppu, discount_mpc, last_30d_mpc, may2_price = k
            except ValueError as e:
                logger.error(f'Error parsing row in {p.url}: {k}')
                logger.exception(e)
                continue
            # same pricelist for all those cash&carry locations
            for loc_id in 'D01 D28 D34 D18 D22 D13 D26 D11 D09'.split():
                resolve_product(prod, barcode, rotodinamic, loc_id, name, discount_mpc or mpc, _qty, may2_price)

    return prod