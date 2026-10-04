import io
import zipfile
from datetime import datetime, date

from loguru import logger
from lxml.etree import tostring

from cijeneorg.fetchers.archiver import WaybackArchiver, PriceList
from cijeneorg.fetchers.common import xpath, extract_offers_since, ensure_archived, get_csv_rows, resolve_product
from cijeneorg.models import Store
from cijeneorg.utils import DDMMYYYY_dots


def fetch_croma_prices(croma: Store, min_date: date):
    # location_id hardcoded as MP
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
        else:
            logger.warning(f'failed to extract date from croma price list link: href={a.get("href")!r} text={a.text_content().strip()!r}')

    actual = extract_offers_since(croma, coll, min_date)
    prod = []
    for p in actual:
        zip_data = ensure_archived(p, True, wayback=False)
        with zipfile.ZipFile(io.BytesIO(zip_data)) as zf:
            for filename in zf.namelist():
                if not filename.endswith('.csv'):
                    continue

                with zf.open(filename) as f:
                    rows = get_csv_rows(f.read())
                    for k in rows:  # no header here
                        if len(k) == 8:
                            name, _id, _, unit, mpc, null, barcode, category = k
                        elif len(k) == 10:
                            name, _id, _, unit, mpc, null, barcode, category, anchored_price, anchored_price_date = k
                        else:
                            logger.warning('cannot parse croma row {}', k)
                            continue
                        if anchored_price_date == '2025-05-02':
                            may2_price = anchored_price
                            sep10_price = None
                        elif anchored_price_date == '2026-09-10':
                            may2_price = None
                            sep10_price = anchored_price
                        else:
                            may2_price = sep10_price = None
                        barcode = barcode.strip('\x00')
                        resolve_product(prod, barcode, croma, p.location_id, name, None, mpc, None, may2_price, p.date)

    return prod
