from angr.procedures.posix.getenv import getenv
from loguru import logger

from cijeneorg.fetchers.archiver import WaybackArchiver, PriceList
from cijeneorg.fetchers.common import xpath, extract_offers_since, get_csv_rows, ensure_archived, resolve_product
from cijeneorg.models import Store
from datetime import datetime, date

def fetch_stridon_prices(stridon: Store, min_date: date):
    WaybackArchiver.archive(index_url := 'https://stridon.hr/hr/supermarketi')
    coll = []

    for href in xpath(index_url, '//a[contains(@href, ".csv")]/@href'):
        filename = href.rsplit('/', 1)[-1]
        location_id, market_type, *address, city, datestr = filename.removesuffix('.csv').split('_')
        address = ' '.join(address)
        dt = datetime.strptime(datestr, '%d%m%Y')
        coll.append(PriceList(href, address, city, stridon.id, location_id, dt, filename))


    # Temporary code, just for archival!
    for value in xpath(index_url, '//option[contains(@value, "Prod.")]/@value'):
        #
        logger.debug(f'found value: {value}')
        for i in range(date(2025, 5, 15).toordinal(), date.today().toordinal()):
            d = datetime.fromordinal(i)
            filename = value + '_' + d.strftime('%d%m%Y') + '.csv'
            full_url = 'https://stridon.hr/cijene-csv/' + filename

            location_id, market_type, *address, city, _ = filename.removesuffix('.csv').split('_')
            p = PriceList(full_url, address, city, stridon.id, location_id, d, filename)
            ensure_archived(p, force=True)
        # p = PriceList(full_url)


    actual = extract_offers_since(stridon, coll, min_date)

    prod = []
    for p in actual:
        rows = get_csv_rows(ensure_archived(p, True, wayback=False))
        for k in rows[1:]:
            name, _id, brand, _qty, units, mpc, ppu, discount_mpc, last_30d_mpc, may2_price, barcode, category = k
            price = discount_mpc.strip() or mpc.strip()
            resolve_product(prod, barcode, stridon, p.location_id, name, brand, price, _qty, may2_price, p.date)

    return prod
