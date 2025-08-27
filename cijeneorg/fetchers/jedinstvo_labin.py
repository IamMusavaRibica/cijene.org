from datetime import datetime, date

from cijeneorg.fetchers.archiver import WaybackArchiver, PriceList
from cijeneorg.fetchers.common import xpath, extract_offers_since, get_csv_rows, ensure_archived, resolve_product
from cijeneorg.models import Store


def fetch_jedinstvo_labin_prices(jedinstvo_labin: Store, min_date: date):
    WaybackArchiver.archive(index_url := 'https://www.jedinstvo-labin.hr/hr/cjenik')
    coll = []
    for href in xpath(index_url, '//a[contains(@href, ".csv")]/@href'):
        filename = href.rsplit('/', 1)[-1]
        market_type, location_name, file_id, date_str = filename.split('_', 3)
        dt = datetime.strptime(date_str, '%Y%m%d_%H%M%S.csv')
        location_id, address, city = {
                                         'TRGOVINA APOLLO Rabac': ('00', 'Obala maršala Tita 24', 'Rabac'),
                                         'MARKET KATURE LABIN': ('01', 'Prilaz Kikova 1-3', 'Labin'),
                                         'MARKET OPSKRBNI CENTAR LABIN': ('02', 'Ermenegilda Štembergera 1b', 'Labin')
                                     }.get(location_name) or ('???', '???', '???')
        coll.append(PriceList(href, address, city, jedinstvo_labin.id, location_id, dt, filename))

    actual = extract_offers_since(jedinstvo_labin, coll, min_date)

    prod = []
    for p in actual:
        rows = get_csv_rows(ensure_archived(p, True, wayback=False))
        for k in rows[1:]:
            name, _id, brand, _qty, unit2, mpc, ppu, barcode, category = map(str.strip, k)
            resolve_product(prod, barcode, jedinstvo_labin, p.location_id, name, mpc, _qty, None, p.date)

    return prod
