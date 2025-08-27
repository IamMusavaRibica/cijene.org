from datetime import datetime, date

from loguru import logger

from cijeneorg.fetchers.archiver import WaybackArchiver, PriceList
from cijeneorg.fetchers.common import xpath, ensure_archived, get_csv_rows, resolve_product, extract_offers_since
from cijeneorg.models import Store


def fetch_radenska_prices(radenska: Store, min_date: date):
    WaybackArchiver.archive(index_url := 'https://www.radenska.hr/cjenici')
    coll = []
    for href in xpath(index_url, '//a[contains(@href, ".csv")]/@href'):
        filename = href.rsplit('/', 1)[-1]
        dt = datetime.strptime(filename, '%Y%m%d.csv')
        coll.append(PriceList(href, 'Ulica Matije Gupca 120', 'Lipik', radenska.id, '0', dt, filename))

    actual = extract_offers_since(radenska, coll, min_date)

    prod = []
    for p in actual:
        rows = get_csv_rows(ensure_archived(p, True, wayback=False))
        for k in rows[1:]:
            name, _id, brand, _qty, unit0, mpc, A_means_discount, base_unit, unit1, ppu, discount_mpc, last_30d_mpc, may2_price, barcode, category = k
            may2_price = may2_price.removeprefix('MPC 2.5.2025=').rstrip('€?')
            resolve_product(prod, barcode, radenska, p.location_id, name, discount_mpc or mpc, _qty, may2_price, p.date)

    return prod
