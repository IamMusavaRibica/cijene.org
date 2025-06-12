from datetime import datetime

from loguru import logger

from cijeneorg.fetchers.archiver import WaybackArchiver, PriceList
from cijeneorg.fetchers.common import xpath, ensure_archived, get_csv_rows, resolve_product, extract_offers_from_today
from cijeneorg.models import Store


def fetch_jadranka_prices(jadranka: Store):
    WaybackArchiver.archive(index_url := 'https://jadranka-trgovina.com/cjenici/')
    coll = []
    pr = 'MARKET_MAXI_DRAZICA5_MALILOSINJ_607_'
    for href in xpath(index_url, '//a[contains(@href, ".csv")]/@href'):
        filename = href.rsplit('/')[-1]
        if not filename.startswith(pr):
            logger.warning(f'unexpected filename: {filename}')
            continue
        dt = datetime.strptime(filename.removeprefix(pr), '%d%m%Y_%H%M.csv')
        coll.append(PriceList(href, 'Dražica 5', 'Mali Lošinj', jadranka.id, '607', dt, filename))

    today_coll = extract_offers_from_today(jadranka, coll)

    prod = []
    for p in today_coll:
        rows = get_csv_rows(ensure_archived(p, True, wayback=False))
        for row in rows:  # no header here
            _id, *name, _, _qty, unit, mpc, ppu, discount_mpc, last_30d_mpc, may2_price, barcode, category = row
            name = ' '.join(name)
            if name.isnumeric():
                name, _id = _id, name
            if barcode.isnumeric():
                resolve_product(prod, barcode, jadranka, p.location_id, name, discount_mpc or mpc, _qty, may2_price)
            elif barcode != '':
                logger.warning(f'failed to parse jadranka row {row}')

    return prod

