from datetime import datetime, date

from loguru import logger

from cijeneorg.fetchers.archiver import PriceList, WaybackArchiver
from cijeneorg.fetchers.common import get_csv_rows, resolve_product, xpath, ensure_archived, extract_offers_since
from cijeneorg.models import Store
from cijeneorg.utils import DDMMYYYY_dots

address_idx = {
    'Hipermarket': ('Optujska ulica 70', 'Varaždin'),
    'Supermarket': ('Ul. Zrinskih i Frankopana 2', 'Varaždin')
}
def fetch_branka_prices(branka: Store, min_date: date):
    WaybackArchiver.archive(INDEX_URL := 'https://branka.hr/cjenik/')
    coll = []
    for a in xpath(INDEX_URL, '//a[contains(@href, ".csv")]'):
        href = a.get('href')
        full_url = 'https://branka.hr/' + href.removeprefix('/')
        orig_filename = href.rsplit('/', 1)[-1]
        if orig_filename == 'Supermarket040426.csv':  # 404
            logger.warning(f'skipping known broken branka price list {orig_filename}')
            continue
        try:
            f = orig_filename
            if f.startswith('Supermarke') and f[10] != 't':  # Supermarke010426.csv
                f = 'Supermarket' + f[10:]
            location_id = f[:11]
            if 'Supermarket' != location_id != 'Hipermarket':
                raise ValueError(f'unexpected location id {location_id} in filename {orig_filename}')
            try:
                dd = int(f[11:13])
                mm = int(f[13:15])
                yyyy = 2000 + int(f[15:17])
            except ValueError:
                # fallback: extract from anchor text, not url
                if m := DDMMYYYY_dots.findall(a.text):
                    logger.debug(f'branka - extracted date from {a.text = } instead of {orig_filename = }')
                    dd, mm, yyyy = map(int, m[0])
                else:
                    raise RuntimeError(f'failed to extract date from filename {orig_filename}')
            dt = datetime(yyyy, mm, dd)
            address, city = address_idx[location_id]
            coll.append(PriceList(full_url, address, city, branka.id, location_id, dt, orig_filename))
        except:
            logger.exception(f'failed to parse filename {orig_filename} for branka')
            continue

    actual = extract_offers_since(branka, coll, min_date)

    prod = []
    for p in actual:
        rows = get_csv_rows(ensure_archived(p, True, wayback=False))
        for k in rows[1:]:
            # brand is often empty in Branka price lists
            _id, name, units, mpc, _qty, barcode, _brand, category, may2_price = k
            resolve_product(prod, barcode, branka, p.location_id, name, None, mpc, _qty, may2_price, p.date)

    return prod
