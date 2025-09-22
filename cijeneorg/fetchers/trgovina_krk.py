from datetime import datetime, date
from urllib.parse import unquote

from loguru import logger

from cijeneorg.fetchers.archiver import WaybackArchiver, PriceList
from cijeneorg.fetchers.common import get_csv_rows, resolve_product, xpath, ensure_archived, extract_offers_since
from cijeneorg.models import Store
from cijeneorg.utils import UA_HEADER, fix_city, fix_address


def fetch_trgovina_krk_prices(trgovina_krk: Store, min_date: date):
    WaybackArchiver.archive(index_url := 'https://trgovina-krk.hr/objava-cjenika/')
    coll = []
    # returns 403 forbidden if we don't use a user-agent. is this legal?
    for href in xpath(index_url, '//a[contains(@href, ".csv")]/@href', extra_headers=UA_HEADER):
        filename = unquote(href).removeprefix('https://trgovina-krk.hr/csv/').removesuffix('.csv')
        fixed = filename.replace('11_A', '11A')
        market_type, address, city, location_id, file_id, datestr = fixed.split('_', 5)
        dt = datetime.strptime(datestr, '%d%m%Y_%H_%M_%S')
        address = fix_address(address)
        city = fix_city(city)
        coll.append(p := PriceList(href, address, city, trgovina_krk.id, location_id, dt, filename))
        p.request_kwargs = {'headers': UA_HEADER}

    actual = extract_offers_since(trgovina_krk, coll, min_date)

    prod = []
    for p in actual:
        rows = get_csv_rows(ensure_archived(p, True, wayback=False))
        parsed_barcodes = set()
        for row in rows[1:]:
            try:
                name, _id, brand, _qty, units, mpc, ppu, discount_mpc, last_30d_mpc, may2_price, barcode, category = row
            except ValueError:
                logger.warning(f'unable to unpack row {row} in {p.url}')
                continue
            if barcode in parsed_barcodes or not barcode:
                continue
            parsed_barcodes.add(barcode)
            name = name.removesuffix(' COCA-COLA').removesuffix(' COCA COLA').removesuffix(' COCA')
            resolve_product(prod, barcode, trgovina_krk, p.location_id, name, brand, discount_mpc or mpc, _qty, may2_price,
                            p.date)

    return prod
