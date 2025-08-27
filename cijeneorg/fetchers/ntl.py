from datetime import datetime, date

from cijeneorg.fetchers.archiver import WaybackArchiver, PriceList
from cijeneorg.fetchers.common import get_csv_rows, resolve_product, xpath, ensure_archived, extract_offers_since
from cijeneorg.models import Store
from cijeneorg.utils import fix_address, fix_city


def fetch_ntl_prices(ntl: Store, min_date: date):
    # comments in the HTML suggest that someone is working on it: https://ibb.co/Vdr4LT0
    WaybackArchiver.archive(index_url := 'https://ntl.hr/cjenik')

    # extract both today's hrefs and the archive hrefs and parse them in the same way
    dates = xpath(index_url, '//select[@id="date"]/option/@value')
    hrefs = []
    for date_str in dates:
        if not date_str:
            continue
        then_url = f'https://ntl.hr/cjenik?date={date_str}'
        year, month, day = map(int, date_str.split('-'))
        date_ = date(year, month, day)
        if date_ >= min_date:
            WaybackArchiver.archive(then_url)
        hrefs1 = xpath(then_url, '//a[contains(@href, ".csv")]/@href')
        hrefs.extend(hrefs1)

    coll = []
    for href in hrefs:
        filename = href.rsplit('/', 1)[-1]
        market_type, address, city, location_id, file_id, rest = filename.split('_', 5)
        if not (location_id.isdigit() and len(location_id) == 5):
            print(f'failed to parse {filename}')
            continue
        dt = datetime.strptime(rest, '%d%m%Y_%H_%M_%S.csv')
        city = fix_city(city)
        address = fix_address(address).replace('Galoviaa', 'Galovića')
        coll.append(PriceList(href, address, city, ntl.id, location_id, dt, filename))

    actual = extract_offers_since(ntl, coll, min_date)

    prod = []
    for p in actual:
        rows = get_csv_rows(ensure_archived(p, True, wayback=True))
        for k in rows[1:]:
            name, _id, brand, _qty, units, mpc, ppu, discount_mpc, last_30d_mpc, may2_price, barcode, category = k
            resolve_product(prod, barcode, ntl, p.location_id, name, discount_mpc or mpc, _qty, may2_price, p.date)

    return prod
