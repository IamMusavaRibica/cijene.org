from datetime import datetime, date

from loguru import logger

from cijeneorg.fetchers.archiver import WaybackArchiver, PriceList
from cijeneorg.fetchers.common import xpath, ensure_archived, get_csv_rows, resolve_product, extract_offers_since
from cijeneorg.models import Store


def fetch_jadranka_prices(jadranka: Store, min_date: date):
    WaybackArchiver.archive(index_url := 'https://jadranka-trgovina.com/cjenici/')
    coll = []
    pr = 'MARKET_MAXI_DRAZICA5_MALILOSINJ_607_'
    for href in xpath(index_url, '//a[contains(@href, ".csv")]/@href'):
        filename = href.rsplit('/')[-1]
        if not filename.removeprefix('02198337590_').startswith(pr):  # OIB prefix since 20.11.2026.
            logger.warning(f'unexpected filename: {filename}')
            continue
        # since 17.11.2026. there is a file id (and since 20.11.2026. also 'ROBA_') before the date
        dt = datetime.strptime('_'.join(filename.rsplit('_', 2)[-2:]), '%d%m%Y_%H%M.csv')
        coll.append(PriceList(href, 'Dražica 5', 'Mali Lošinj', jadranka.id, '607', dt, filename))

    actual = extract_offers_since(jadranka, coll, min_date)

    prod = []
    for p in actual:
        rows = get_csv_rows(ensure_archived(p, True, wayback=False))
        if rows and rows[0][0] == 'NAZIV ROBE':  # since 20.11.2026. MPC;POSEBAN OBLIK PRODAJE;CIJENA ZA JM;BAR KOD;EAN KOD;BAZNA CIJENA;
            for name, _id, brand, _qty, unit, mpc, discount_name, ppu, _barkod, barcode, base_price, *_ in rows[1:]:
                resolve_product(prod, barcode, jadranka, p.location_id, name, brand, mpc, _qty, None, p.date)
            continue
        for row in rows:  # no header here
            if len(row) == 9:  # 17.-19.11.2026. only header (without regular MPC), no rows
                continue
            _id, *name, _, _qty, unit, mpc, ppu, discount_mpc, last_30d_mpc, may2_price, barcode, category = row
            name = ' '.join(name)
            if name.isnumeric():
                name, _id = _id, name
            if barcode.isnumeric():
                resolve_product(prod, barcode, jadranka, p.location_id, name, None, discount_mpc or mpc, _qty, may2_price,
                                p.date)
            elif barcode != '':
                logger.warning(f'failed to parse jadranka row {row}')

    return prod
