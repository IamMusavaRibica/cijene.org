import io
import re
import zipfile
from datetime import datetime, date

from loguru import logger

from cijeneorg.fetchers.archiver import WaybackArchiver, PriceList
from cijeneorg.fetchers.common import get_csv_rows, resolve_product, xpath, ensure_archived, extract_offers_since
from cijeneorg.models import Store
from cijeneorg.utils import fix_address, fix_city


def fetch_plodine_prices(plodine: Store, min_date: date):
    WaybackArchiver.archive(index_url := 'https://www.plodine.hr/info-o-cijenama')
    coll = []
    for href in xpath(index_url, '//a[contains(@href, "plodine.hr/cjenici/")]/@href',
                      verify='certs/www.plodine.hr.crt'):
        filename = href.rsplit('/', 1)[-1]
        if not filename.endswith('.zip'):
            logger.warning(f'unexpected file href in Plodine prices page: {href}')
            continue
        dt = datetime.strptime(filename, 'cjenici_%d_%m_%Y_%H_%M_%S.zip')
        coll.append(PriceList(href, None, None, plodine.id, None, dt, filename))

    actual = extract_offers_since(plodine, coll, min_date)

    prod = []
    for p in actual:
        zip_data = ensure_archived(p, True, wayback=False)
        with zipfile.ZipFile(io.BytesIO(zip_data)) as zf:
            for filename in zf.namelist():
                if not filename.endswith('.csv'):
                    logger.warning(f'unexpected file in Plodine zip: {filename}')
                    continue

                market_type, *full_addr, store_id, _id, _ = filename.split('_')
                full_addr = ' '.join(full_addr)
                five_digit_nums = list(re.finditer(r'\b\d{5}\b', full_addr))
                if not five_digit_nums:
                    logger.warning(f'failed to parse filename {filename}')
                    continue

                postal_match = five_digit_nums[-1]
                address = full_addr[:postal_match.start()].strip()
                postal_code = postal_match.group(0)
                city = full_addr[postal_match.end():].strip().title()
                city = fix_city(city)
                address = fix_address(address)

                with zf.open(filename) as f:
                    rows = get_csv_rows(f.read())
                    for k in rows[1:]:
                        name, _id, brand, _qty, units, mpc, ppu, discount_mpc, last_30d_mpc, may2_price, barcode, category, *_ = k
                        resolve_product(prod, barcode, plodine, store_id, name, discount_mpc or mpc, _qty, may2_price,
                                        p.date)
    return prod
