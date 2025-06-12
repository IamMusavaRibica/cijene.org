from datetime import datetime

from loguru import logger

from cijeneorg.fetchers.archiver import WaybackArchiver, Pricelist
from cijeneorg.fetchers.common import xpath, ensure_archived, get_csv_rows, resolve_product, extract_offers_from_today
from cijeneorg.models import Store


def fetch_radenska_prices(radenska: Store):
    WaybackArchiver.archive(index_url := 'https://www.radenska.hr/cjenici')
    coll = []
    for href in xpath(index_url, '//a[contains(@href, ".csv")]/@href'):
        filename = href.rsplit('/', 1)[-1]
        dt = datetime.strptime(filename, '%Y%m%d.csv')
        coll.append(Pricelist(href, 'Ulica Matije Gupca 120', 'Lipik', radenska.id, '0', dt, filename))

    today_coll = extract_offers_from_today(radenska, coll)

    prod = []
    for p in today_coll:
        rows = get_csv_rows(ensure_archived(p, True, wayback=False))
        for k in rows[1:]:
            name, _id, brand, _qty, unit0, mpc, A_means_discount, base_unit, unit1, ppu, discount_mpc, last_30d_mpc, may2_price, barcode, category = k
            may2_price = may2_price.removeprefix('MPC 2.5.2025=').rstrip('€?')
            resolve_product(prod, barcode, radenska, p.location_id, name, discount_mpc or mpc, _qty, may2_price)

    return prod
