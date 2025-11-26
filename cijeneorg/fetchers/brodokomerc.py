from datetime import datetime, date

from cijeneorg.fetchers.archiver import WaybackArchiver, PriceList
from cijeneorg.fetchers.common import xpath, ensure_archived, get_csv_rows, resolve_product, extract_offers_since
from cijeneorg.models import Store
from cijeneorg.utils import fix_address


def fetch_brodokomerc_prices(brodokomerc: Store, min_date: date):
    WaybackArchiver.archive(index_url := 'http://www.brodokomerc.hr/cijene')
    coll = []
    for href in xpath(index_url, '//a[contains(@href, ".csv")]/@href'):
        idx = 1 + (not href.endswith('.csv'))
        filename = href.rsplit('/', idx)[-idx]
        href = 'http://www.brodokomerc.hr' + href
        market_type, address, city, location_id, file_id, date_str = filename.split('_', 5)
        address = {
                      'ZRINSKI+TRG+BB': 'Zrinski trg bb',
                      'CANDEKOVA+32': 'Candekova 32',
                      'DRAZICKIH+BORACA+BB': 'Dražičkih boraca bb',
                      'KVATERNIKOVA+65': 'Kvaternikova 65',
                      'F.+BELULOVICA+5.': 'Ulica Franje Belulovića 5',
                  }.get(address) or fix_address(address.replace('+', ' '))
        date_str = date_str.replace('_', '')
        #                      fix 16112025071919+%281%29.csv
        dt = datetime.strptime(date_str.split('+')[0].removesuffix('.csv'), '%d%m%Y%H%M%S')
        coll.append(PriceList(href, address, city, brodokomerc.id, location_id, dt, filename))

    actual = extract_offers_since(brodokomerc, coll, min_date)

    prod = []
    for p in actual:
        rows = get_csv_rows(ensure_archived(p, True, wayback=False))
        for k in rows[1:]:
            name, _id, brand, _qty, unit, mpc, ppu, discount_mpc, last_30d_mpc, may2_price, barcode, category = k
            resolve_product(prod, barcode, brodokomerc, p.location_id, name, brand, discount_mpc or mpc, _qty, may2_price,
                            p.date)

    return prod
