from datetime import datetime, date

from cijeneorg.fetchers.archiver import WaybackArchiver, PriceList
from cijeneorg.fetchers.common import xpath, ensure_archived, get_csv_rows, resolve_product, extract_offers_since
from cijeneorg.models import Store

BASE_URL = 'https://cs-nv.ddns.net/cjenici/'


def fetch_dergez_prices(dergez: Store, min_date: date):
    # one price list for all stores (ZA_SVA_PRODAJNA_MJESTA), location_id hardcoded as X
    WaybackArchiver.archive(index_url := BASE_URL + 'index.php?oib=10948162678')
    coll = []
    for href in xpath(index_url, '//a[contains(@href, "download.php")]/@href'):
        filename = href.rsplit('file=', 1)[-1]  # 10948162678_ZA_SVA_PRODAJNA_MJESTA_ROBA_20261119_1124.csv
        dt = datetime.strptime('_'.join(filename.rsplit('_', 2)[-2:]), '%Y%m%d_%H%M.csv')
        coll.append(PriceList(BASE_URL + href, None, None, dergez.id, 'X', dt, filename))

    actual = extract_offers_since(dergez, coll, min_date)

    prod = []
    for p in actual:
        # some names contain a lone \r, e.g. 'PLIN ZA UPALJAČE 100\rML ELICO'
        rows = get_csv_rows(ensure_archived(p, True, wayback=False).replace(b'\r\n', b'\n').replace(b'\r', b' '))
        for k in rows[1:]:
            _id, name, brand, _qty, unit, mpc, ppu, barcode, ean, base_price = k
            resolve_product(prod, barcode or ean, dergez, p.location_id, name, None, mpc, None, None, p.date)

    return prod
