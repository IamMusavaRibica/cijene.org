import re
from datetime import datetime, date

from loguru import logger

from cijeneorg.fetchers.archiver import PriceList, WaybackArchiver
from cijeneorg.fetchers.common import xpath, ensure_archived, get_csv_rows, resolve_product, extract_offers_since
from cijeneorg.models import Store
from cijeneorg.utils import fix_city


def fetch_bakmaz_prices(bakmaz: Store, min_date: date):
    WaybackArchiver.archive(index_url := 'https://www.bakmaz.hr/o-nama/')
    coll = []
    for url in xpath(index_url, '//a[@class="btn-preuzmi"]/@href'):
        filename = url.rsplit('/', 1)[-1]
        if not filename.endswith('.csv'):
            logger.warning(f'unexpected non-csv href: {url}')
            continue
        try:
            market_type, address, city, location_id, file_id, dtstr = filename.split('_', 5)
            address = address.replace('-', ' ')
            city = fix_city(city)
            dtstr = dtstr.replace('_', '')
            idx = 0
            if m := re.search(r'-(\d+)\.csv', dtstr):
                idx = int(m.group(1))  # multiple files have (1).csv which is -1.csv in the url

            # TODO: this results in duplicate entries per product and store_id
            files = 0
            while idx >= 0:
                files += 1
                new_url = re.sub(r'-(\d+)\.csv', '.csv' if idx == 0 else f'-{idx}.csv', url)
                if files > 1:
                    logger.info(f'extra bakmaz url: {new_url}')
                dt = datetime.strptime(dtstr.replace('_', '').removesuffix('.csv').split('-')[0], '%d%m%Y%H%M%S')
                coll.append(PriceList(url, address, city, bakmaz.id, location_id, dt, filename))
                idx -= 1

        except Exception as e:
            logger.warning(f'error {e!r} while bakmaz pricelist {filename = }')
            logger.exception(e)
            continue

    actual = extract_offers_since(bakmaz, coll, min_date, wayback=False)

    prod = []
    for t in actual:
        rows = get_csv_rows(ensure_archived(t, True, wayback=False))
        for k in rows[1:]:
            name, _id, brand, _qty, units, mpc, ppu, discount_mpc, last_30d_mpc, may2_price, barcode, category = k
            resolve_product(prod, barcode, bakmaz, t.location_id, name, brand, discount_mpc or mpc, _qty, may2_price, t.date)

    return prod
