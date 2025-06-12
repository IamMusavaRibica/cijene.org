from datetime import datetime

from cijeneorg.fetchers.archiver import WaybackArchiver, PriceList
from cijeneorg.fetchers.common import xpath, extract_offers_from_today, get_csv_rows, ensure_archived, resolve_product
from cijeneorg.models import Store
from cijeneorg.utils import DDMMYYYY_dots


def fetch_travelfree_prices(travelfree: Store):
    # https://travelfree.hr/vinjani-donji/objava-cjenika
    # https://travelfree.hr/modules/vtanchorprice/output/Gruda/Gruda_23052025010002.csv
    # also look at https://web.archive.org/web/20250000000000*/https://travelfree.hr/vinjani-donji/objava-cjenika
    WaybackArchiver.archive(index_url := 'https://travelfree.hr/objava-cjenika')
    coll = []
    for a in xpath(index_url, '//a[contains(@href, ".csv")]'):
        city, date_str = a.text.strip().split('_')
        dt = datetime.strptime(date_str, '%d%m%Y%H%M%S.csv')
        url = 'https://travelfree.hr' + a.get('href')  # a.attrib['href']
        filename = url.rsplit('/', 1)[-1]
        location_id, address = {
            'Novi Varoš': '00 Novi Varoš 35',
            'Vinjani Donji': '01 Vinjani Donji 567',
            'Gruda': '02 Tušići 15 (Jadranska Magistrala)',
            'Županja': '03 D55 bb (benzinska postaja BDM Minavci)'
        }.get(city, '?? nepoznato').split(maxsplit=1)
        coll.append(PriceList(url, address, city, travelfree.id, location_id, dt, filename))

    today_coll = extract_offers_from_today(travelfree, coll, wayback=True)

    prod = []
    for p in today_coll:
        rows = get_csv_rows(ensure_archived(p, True))
        for k in rows[1:]:
            name, _id, brand, _qty, unit, mpc, ppu, barcode, category = k
            resolve_product(prod, barcode, travelfree, p.location_id, name, mpc, _qty, None)

    return prod
