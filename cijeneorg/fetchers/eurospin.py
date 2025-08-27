import io
import zipfile
from datetime import datetime, date

from loguru import logger

from cijeneorg.fetchers.archiver import PriceList, WaybackArchiver
from cijeneorg.fetchers.common import get_csv_rows, resolve_product, xpath, ensure_archived, extract_offers_since
from cijeneorg.models import Store
from cijeneorg.utils import DDMMYYYY_dots, fix_city


def fetch_eurospin_prices(eurospin: Store, min_date: date):
    WaybackArchiver.archive(index_url := 'https://www.eurospin.hr/cjenik/')
    coll = []
    for option in xpath(index_url, '//option[contains(@value, "cjenik")]'):
        if m := DDMMYYYY_dots.findall(filename := option.text.strip()):
            day, month, year = map(int, *m)
            dd = datetime(year, month, day)
            coll.append(PriceList(option.get('value'), None, None, eurospin.id, None, dd, filename))

    actual = extract_offers_since(eurospin, coll, min_date)

    prod = []
    for p in actual:
        zip_data = ensure_archived(p, True)  # Wayback Machine 'Capture outlinks' does not capture these .zip files
        with zipfile.ZipFile(io.BytesIO(zip_data)) as zf:
            for filename in zf.namelist():
                if not filename.endswith('.csv'):
                    logger.warning(f'unexpected file in Eurospin zip: {filename}')
                    continue
                market_type, location_id, *full_addr, city, postal_code, _id, _date, _ = filename.split('-')
                city = fix_city(city.replace('_', ' '))
                address = ' '.join(full_addr).replace('_', ' ')

                with zf.open(filename) as f:
                    rows = get_csv_rows(f.read())
                    for k in rows[1:]:
                        name, _id, brand, _qty, units, mpc, ppu, discount_mpc, _, last_30d_mpc, may2_price, barcode, category = k
                        resolve_product(prod, barcode, eurospin, location_id, name, discount_mpc or mpc, _qty, may2_price, p.date)

    return prod