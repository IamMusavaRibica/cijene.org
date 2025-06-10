from datetime import datetime

from loguru import logger

from cijenelib.fetchers._archiver import WaybackArchiver, Pricelist
from cijenelib.fetchers._common import xpath, ensure_archived, get_csv_rows, resolve_product
from cijenelib.models import Store


def fetch_jadranka_prices(jadranka: Store):
    WaybackArchiver.archive(index_url := 'https://jadranka-trgovina.com/cjenici/')
    coll = []
    pr = 'MARKET_MAXI_DRAZICA5_MALILOSINJ_607_'
    for href in xpath(index_url, '//a[contains(@href, ".csv")]/@href', verify='certs/jadranka-trgovina-com-chain.pem'):
        filename = href.rsplit('/')[-1]
        if not filename.startswith(pr):
            logger.warning(f'unexpected filename: {filename}')
            continue
        dt = datetime.strptime(filename.removeprefix(pr), '%d%m%Y_%H%M.csv')
        coll.append(Pricelist(href, 'Dražica 5', 'Mali Lošinj', jadranka.id, '607', dt, filename))

    if not coll:
        logger.warning('no jadranka prices found')
        return []

    logger.info(f'found {len(coll)} jadranka pricelists')
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

