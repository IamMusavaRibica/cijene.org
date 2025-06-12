import io
import zipfile
from datetime import datetime

from lxml.etree import tostring

from cijeneorg.fetchers.archiver import WaybackArchiver, PriceList
from cijeneorg.fetchers.common import xpath, extract_offers_from_today, ensure_archived, get_csv_rows, resolve_product
from cijeneorg.models import Store
from cijeneorg.utils import DDMMYYYY_dots


def fetch_croma_prices(croma: Store):
    WaybackArchiver.archive(index_url := 'https://croma.com.hr/maloprodaja/')
    coll = []
    for a in xpath(index_url, '//a[contains(@href, ".zip")]'):
        inner_html = b''.join([tostring(child) for child in a]).decode()
        if m := DDMMYYYY_dots.search(inner_html):
            day, month, year = map(int, m.groups())
            dt = datetime(year, month, day)
            href = a.get('href')
            filename = href.rsplit('/', 1)[-1]
            coll.append(PriceList(href, 'Ulica Vilima Cecelja 6', 'Sveti Ilija', croma.id, 'MP', dt, filename))

    today_coll = extract_offers_from_today(croma, coll)
    prod = []
    for p in today_coll:
        zip_data = ensure_archived(p, True, wayback=False)
        with zipfile.ZipFile(io.BytesIO(zip_data)) as zf:
            for filename in zf.namelist():
                if not filename.endswith('.csv'):
                    continue

                with zf.open(filename) as f:
                    rows = get_csv_rows(f.read())
                    for k in rows:  # no header here
                        name, _id, _, unit, mpc, null, barcode, category = k
                        resolve_product(prod, barcode, croma, p.location_id, name, mpc, None, None)

    return prod
