from datetime import datetime, date

from cijeneorg.fetchers.archiver import WaybackArchiver, PriceList
from cijeneorg.fetchers.common import xpath, ensure_archived, extract_offers_since, get_csv_rows, resolve_product
from cijeneorg.models import Store


def fetch_tobylex_prices(tobylex: Store, min_date: date):
    # https://tobylex.net/testna-stranica/
    # adresa je Froudeova 34, 10020 Zagreb, ali je virtualna trgovina
    WaybackArchiver.archive(index_url := 'https://tobylex.net/cjenik/')
    coll = []
    for xml_href in xpath(index_url, '//a[contains(@href, ".xml")]/@href'):
        filename = xml_href.rsplit('/', 1)[-1]
        dt = datetime.strptime(filename, 'cjenik_%Y%m%d_%H%M%S.xml')
        ensure_archived(PriceList(xml_href, '(internet trgovina)', '', tobylex.id, 'WEBSHOP', dt, filename))

    for csv_href in xpath(index_url, '//a[contains(@href, ".csv")]/@href'):
        filename = csv_href.rsplit('/', 1)[-1]
        dt = datetime.strptime(filename, 'cjenik_%Y%m%d_%H%M%S.csv')
        coll.append(PriceList(csv_href, '(internet trgovina)', '', tobylex.id, 'WEBSHOP', dt, filename))

    actual = extract_offers_since(tobylex, coll, min_date)

    prod = []
    for p in actual:
        rows = get_csv_rows(ensure_archived(p, True, wayback=False))
        for k in rows[1:]:
            val1, val2, name, mpc = k
            barcode = val1 or val2
            if barcode:
                resolve_product(prod, barcode, tobylex, 'WEBSHOP', name, mpc, None, None, p.date)

    return prod