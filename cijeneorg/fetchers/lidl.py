import io
import zipfile
from datetime import datetime

from loguru import logger

from cijeneorg.fetchers.archiver import PriceList, WaybackArchiver
from cijeneorg.fetchers.common import get_csv_rows, resolve_product, xpath, ensure_archived, extract_offers_from_today
from cijeneorg.models import Store
from cijeneorg.utils import DDMMYYYY_dots, fix_city


def fetch_lidl_prices(lidl: Store):
    WaybackArchiver.archive(index_url := 'https://tvrtka.lidl.hr/cijene')
    coll = []
    for p in xpath(index_url, '//a[starts-with(@href, "https://tvrtka.lidl.hr/content/download/")]/..'):
        if m := DDMMYYYY_dots.findall(p.text):
            day, month, year = map(int, *m)
            dt = datetime(year, month, day)
            href ,= p.xpath('a/@href')
            filename = href.rsplit('/', 1)[-1]
            coll.append(PriceList(href, None, None, lidl.id, None, dt, filename))

    today_coll = extract_offers_from_today(lidl, coll, wayback=True)

    prod = []
    for p in today_coll:
        zip_data = ensure_archived(p, True)
        with zipfile.ZipFile(io.BytesIO(zip_data)) as zf:
            for filename in zf.namelist():
                if not filename.endswith('.csv'):
                    logger.warning(f'unexpected file in lidl zip: {filename}')
                    continue

                market_type, location_id, *full_addr, city, postal_code, _id, _date, _ = filename.split('_')
                city = fix_city(city.replace('_', ' '))
                address = ' '.join(full_addr).replace('_', ' ')

                with zf.open(filename) as f:
                    rows = get_csv_rows(f.read())
                    for k in rows[1:]:
                        # index 3: neto kolicina, but it is weird
                        name, _id, _qty, _, brand, mpc, discount_mpc, last_30d_mpc, ppu, barcode, category, may2_price = k
                        if not may2_price or 'Nije_bilo' in may2_price:
                            may2_price = None
                        resolve_product(prod, barcode, lidl, location_id, name, discount_mpc or mpc, _qty, may2_price)

    return prod