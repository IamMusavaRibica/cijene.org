import re
from datetime import datetime, date

from loguru import logger

from cijeneorg.fetchers.archiver import WaybackArchiver, PriceList
from cijeneorg.fetchers.common import xpath, ensure_archived, get_csv_rows, resolve_product, extract_offers_since
from cijeneorg.models import Store
from cijeneorg.utils import fix_address, DDMMYYYY_dots, fix_city


def fetch_dukat_prices(dukat: Store, min_date: date):
    WaybackArchiver.archive(index_url := 'https://dukat.hr/diskonti')
    coll = []

    for a in xpath(index_url, '//a[contains(@href, ".csv")]'):
        href = a.get('href')
        filename = href.rsplit('/', 1)[-1]
        full_url = 'https://dukat.hr/' + href.removeprefix('/')
        a_text = ''.join(a.itertext()).strip() or a[0][0].tail

        try:
            dd1 = dd2 = mm1 = mm2 = yyyy1 = yyyy2 = HH = MM = None
            if m := re.search(r'(\d\d)[._-](\d\d)[._-](20\d\d)[._-](\d\d)[._-](\d\d)', filename):
                dd1, mm1, yyyy1, HH, MM = map(int, m.groups())
            if m := DDMMYYYY_dots.search(a_text):
                dd2, mm2, yyyy2 = map(int, m.groups())
                HH = 7
                MM = 0
            if dd1 is None and dd2 is None:
                raise RuntimeError('no date info found')
            # check for mismatch
            for t1, t2 in ((dd1, dd2), (mm1, mm2), (yyyy1, yyyy2)):
                if t1 and t2 and t1 != t2:
                    raise ValueError(f'inconsistent date info in filename and anchor text: {filename} {a_text}')
            dd = dd1 or dd2
            mm = mm1 or mm2
            yyyy = yyyy1 or yyyy2
            dt = datetime(yyyy, mm, dd, HH, MM)
            location_name, address, city = a_text.split('-')[-1].split(', ')
            location_id = filename.split('-')[-7]
            coll.append(PriceList(full_url, fix_address(address), fix_city(city), dukat.id, location_id, dt, filename))
        except:
            logger.exception(f'failed to parse dukat price list: {a_text} {filename}')

    actual = extract_offers_since(dukat, coll, min_date)

    prod = []
    for p in actual:
        rows = get_csv_rows(ensure_archived(p, True, wayback=False))
        for k in rows[1:]:
            name, _id, brand, _qty, units, mpc, ppu, discount_mpc, last_30d_mpc, may2_price, barcode, category = k
            resolve_product(prod, barcode, dukat, p.location_id, name, brand, discount_mpc or mpc, _qty, may2_price,
                            p.date)

    return prod
