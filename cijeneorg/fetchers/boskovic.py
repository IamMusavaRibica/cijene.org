from datetime import datetime, date
from urllib.parse import unquote

from cijeneorg.fetchers.archiver import WaybackArchiver, PriceList
from cijeneorg.fetchers.common import xpath, ensure_archived, get_csv_rows, resolve_product, extract_offers_since
from cijeneorg.models import Store
from cijeneorg.utils import fix_address, fix_city


def fetch_boskovic_prices(boskovic: Store, min_date: date):
    WaybackArchiver.archive(index_url := 'https://slavonija-boskovic.hr/wp-content/uploads/cjenici/')
    coll = []
    for href in xpath(index_url, '//a[starts-with(@href, "Cjenik_")]/@href'):
        filename = unquote(href)  # Cjenik_PJ01 CERNA_J.J. STROSSMAYERA 23_CERNA_20261122.CSV
        _, pj, *address, city, date_str = filename.split('_')
        location_id = pj.split()[0]
        dt = datetime.strptime(date_str.upper(), '%Y%m%d.CSV')
        coll.append(PriceList(index_url + href, fix_address(' '.join(address)), fix_city(city), boskovic.id, location_id,
                              dt, filename))

    actual = extract_offers_since(boskovic, coll, min_date)

    prod = []
    for p in actual:
        rows = get_csv_rows(ensure_archived(p, True, wayback=False))
        for k in rows[1:]:
            name, _id, brand, unit, ppu, mpc, is_discount, discount_name, anchor_price, barcode, availability = k
            # MPC_Cijena already includes the discount, Sidrena_cijena has no date so it is not used as may2_price
            resolve_product(prod, barcode, boskovic, p.location_id, name, brand, mpc, None, None, p.date)

    return prod
