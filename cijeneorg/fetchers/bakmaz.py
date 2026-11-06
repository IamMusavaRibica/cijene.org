from datetime import datetime, date
from urllib.parse import quote

import requests
from loguru import logger

from cijeneorg.fetchers.archiver import PriceList, WaybackArchiver
from cijeneorg.fetchers.common import ensure_archived, get_csv_rows, resolve_product, extract_offers_since
from cijeneorg.models import Store
from cijeneorg.utils import fix_city


def fetch_bakmaz_prices(bakmaz: Store, min_date: date):
    WaybackArchiver.archive('https://www.bakmaz.hr/cjenici')
    WaybackArchiver.archive(index_url := 'https://www.bakmaz.hr/api/cjenici.php')
    coll = []
    for entry in requests.get(index_url, timeout=60).json():
        filename = entry['file_name']
        if not filename.endswith('.csv'):
            logger.warning(f'unexpected non-csv file: {filename}')
            continue
        try:
            url = f'https://www.bakmaz.hr/cjenik/{quote(filename)}'
            address = entry['address']
            city = fix_city(entry['city'])
            location_id = entry['store_code']
            dtstr = filename.split('_', 5)[-1].replace('_', '').removesuffix('.csv')
            dt = datetime.strptime(dtstr, '%d%m%Y%H%M%S')
            coll.append(PriceList(url, address, city, bakmaz.id, location_id, dt, filename))

        except Exception as e:
            logger.warning(f'error {e!r} while bakmaz pricelist {filename = }')
            logger.exception(e)
            continue

    actual = extract_offers_since(bakmaz, coll, min_date, wayback=True)

    prod = []
    for t in actual:
        rows = get_csv_rows(ensure_archived(t, True, wayback=False))
        header = ';'.join(rows[0])
        # logger.debug(f'header: {header}')
        for k in rows[1:]:
            if header == 'Naziv proizvoda;Šifra proizvoda;Marka proizvoda;Neto količina;Jedinica mjere;Maloprodajna cijena;Naziv posebnog oblika prodaje;Cijena za jedinicu mjere;Sidrena cijena;Barkod;Kategorija proizvoda;Dostupnost':
                name, _id, brand, _qty, units, mpc, discount_name, ppu, anchor_price, barcode, category, availability = k
                discount_mpc = None
                may2_price = None
            else:
                name, _id, brand, _qty, units, mpc, ppu, discount_mpc, last_30d_mpc, may2_price, barcode, category = k
            resolve_product(prod, barcode, bakmaz, t.location_id, name, brand, discount_mpc or mpc, _qty, may2_price, t.date)

    return prod