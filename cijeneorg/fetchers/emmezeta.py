import re
from datetime import datetime, date

from loguru import logger

from cijeneorg.fetchers.archiver import PriceList, WaybackArchiver
from cijeneorg.fetchers.common import get_csv_rows, resolve_product, xpath, ensure_archived, extract_offers_since
from cijeneorg.models import Store
from cijeneorg.utils import DDMMYYYY_dots


def fetch_emmezeta_prices(emmezeta: Store, min_date: date):
    WaybackArchiver.archive(BASE_URL := 'https://s3.emmezeta.hr/csv/csv_list.html')
    coll = []
    for full_url in xpath(BASE_URL, '//a[contains(@href, ".csv")]/@href'):
        filename = full_url.rsplit('/', 1)[-1]
        if '_USLUGE_' in filename:  # since 17.11.2026. services (USLUGE) are published separately from goods (ROBA)
            continue
        try:
            # since 17.11.2026.: Emmezeta__30777726033_Specijalizirana-prodavaonica-neprehrambenih-proizvoda_Svilajska-36_OS_ROBA_7_20261121_0012.csv
            parse_name = re.sub(r'^Emmezeta__?\d{11}_.*_([^_]+)_ROBA_\d+_(20\d\d)(\d\d)(\d\d)_(\d\d)\d\d', r'Emmezeta_\1_ROBA_\4.\3.\2_\5', filename)
            date_str = (parse_name.removeprefix('Emmezeta_')
                        .removesuffix('.csv')
                        )
            if not date_str[0].isdigit():
                location_id, ser, date_str = date_str.split('_', maxsplit=2)
            else:
                location_id = '???'

            if m := DDMMYYYY_dots.findall(date_str):
                dd, mm, yyyy = map(int, m[0])
            elif '25072025' in filename:
                dd, mm, yyyy = 25, 7, 2025
            else:
                raise RuntimeError(f'failed to extract date from filename {date_str}')

            dt = datetime(yyyy, mm, dd)
            coll.append(PriceList(full_url, '???', '???', emmezeta.id, location_id, dt, filename))
        except:
            logger.exception(f'failed to parse filename {filename} for emmezeta')
            continue

    actual = extract_offers_since(emmezeta, coll, min_date)

    prod = []
    for p in actual:
        rows = get_csv_rows(ensure_archived(p, True, wayback=False))
        for k in rows[1:]:
            if len(k) == 14:
                name, _id, brand, category, units, _qty, mpc, _mass, _3d, _h, _w, barcode, last_30d_mpc, may2_price = k
            elif len(k) == 15:
                name, _id, mpc, brand, category, _qty, _mass, _3d, _h, _w, barcode, units, last_30d_mpc, may2_price, sep10_price = k
            elif len(k) == 13:  # since 17.11.2026. no separate discount price, MPC is the current price
                name, _id, brand, _qty, units, mpc, is_discount, ppu, val1, val2, base_price, may2_price, sep10_price = k
                barcode = val1 or val2
            else:
                logger.warning('cannot parse emmezeta row {}', k)
                break
            resolve_product(prod, barcode, emmezeta, p.location_id, name, brand, mpc, _qty, may2_price, p.date)

    return prod
