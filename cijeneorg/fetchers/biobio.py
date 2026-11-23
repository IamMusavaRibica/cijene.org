import re
from datetime import datetime, date

from cijeneorg.fetchers.archiver import WaybackArchiver, PriceList
from cijeneorg.fetchers.common import xpath, ensure_archived, get_csv_rows, resolve_product, extract_offers_since
from cijeneorg.models import Store


def fetch_biobio_prices(biobio: Store, min_date: date):
    # only the webshop price list, location_id hardcoded as web
    # NOTE: as of 22.11.2026. the barkod column is always empty, so no products can be matched
    WaybackArchiver.archive(index_url := 'https://www.biobio.hr/cjenik-proizvoda/')
    coll = []
    for href in set(xpath(index_url, '//a[contains(@href, ".csv")]/@href')):
        filename = href.rsplit('/', 1)[-1]  # proizvodi-web-webshop-web-11-20261122T010949.csv
        if not (m := re.search(r'-(20\d{6}T\d{6})\.csv$', filename)):
            continue
        dt = datetime.strptime(m.group(1), '%Y%m%dT%H%M%S')
        coll.append(PriceList(href, None, None, biobio.id, 'web', dt, filename))

    actual = extract_offers_since(biobio, coll, min_date)

    prod = []
    for p in actual:
        rows = get_csv_rows(ensure_archived(p, True, wayback=False))
        for k in rows[1:]:
            name, _id, brand, unit, ppu, mpc, is_discount, discount_name, anchor_price, barcode, availability = k
            # sidrena_cijena has no date, so it is not used as may2_price
            resolve_product(prod, barcode, biobio, p.location_id, name, brand, mpc, None, None, p.date)

    return prod
