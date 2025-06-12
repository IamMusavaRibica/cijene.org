from datetime import datetime

from loguru import logger

from cijeneorg.fetchers.archiver import WaybackArchiver, Pricelist
from cijeneorg.fetchers.common import xpath, ensure_archived, get_csv_rows, resolve_product, extract_offers_from_today
from cijeneorg.models import Store
from cijeneorg.utils import fix_address


def fetch_brodokomerc_prices(brodokomerc: Store):
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
        dt = datetime.strptime(date_str, '%d%m%Y%H%M%S.csv')
        coll.append(Pricelist(href, address, city, brodokomerc.id, location_id, dt, filename))

    today_coll = extract_offers_from_today(brodokomerc, coll)

    prod = []
    for p in today_coll:
        rows = get_csv_rows(ensure_archived(p, True, wayback=False))
        for k in rows[1:]:
            name, _id, brand, _qty, unit, mpc, ppu, discount_mpc, last_30d_mpc, may2_price, barcode, category = k
            resolve_product(prod, barcode, brodokomerc, p.location_id, name, discount_mpc or mpc, _qty, may2_price)

    return prod