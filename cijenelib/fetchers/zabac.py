from datetime import datetime

from loguru import logger

from cijenelib.fetchers._archiver import WaybackArchiver, Pricelist
from cijenelib.fetchers._common import xpath, ensure_archived, get_csv_rows, resolve_product
from cijenelib.models import Store
from cijenelib.utils import fix_address

extra_urls = '''
https://zabacfoodoutlet.hr/wp-content/uploads/2025/05/Cjenik-Zabac-Food-Outlet-PJ-2-Tratinska-80A.csv
https://zabacfoodoutlet.hr/wp-content/uploads/2025/05/Cjenik-Zabac-Food-Outlet-PJ-4-Nemciceva-1.csv
https://zabacfoodoutlet.hr/wp-content/uploads/2025/05/Cjenik-Zabac-Food-Outlet-PJ-5-Bozidara-Magovca.csv
https://zabacfoodoutlet.hr/wp-content/uploads/2025/05/Cjenik-Zabac-Food-Outlet-PJ-6-Dolac-2.csv
https://zabacfoodoutlet.hr/wp-content/uploads/2025/05/Cjenik-Zabac-Food-Outlet-PJ-7-DUbrava-256L.csv
https://zabacfoodoutlet.hr/wp-content/uploads/2025/05/Cjenik-Zabac-Food-Outlet-PJ-9-Ilica-231.csv
https://zabacfoodoutlet.hr/wp-content/uploads/2025/05/Cjenik-Zabac-Food-Outlet-PJ-10-Zagrebacka-Cesta-205.csv
https://zabacfoodoutlet.hr/wp-content/uploads/2025/05/Cjenik-Zabac-Food-Outlet-PJ-11-Savska-Cesta-206.csv
'''
def fetch_zabac_prices(zabac: Store):
    coll = []
    WaybackArchiver.archive('https://zabacfoodoutlet.hr/cjenik/')  # just in case
    for url in xpath('https://zabacfoodoutlet.hr/cjenik/', '//a[contains(@href, ".csv")]/@href'):
        try:
            filename = url.rsplit('/', 1)[-1]
            address, datestr = filename.removeprefix('Cjenik-').rsplit('-', 1)
            address = fix_address(address.replace('-', ' '))
            dt = datetime.strptime(datestr, '%d%m%Y.csv')
            coll.append(Pricelist(url, address, 'Zagreb', zabac.id, 'PJ-?', dt, filename))
        except Exception as e:
            logger.warning(f'failed to parse zabac pricelists: {url}')
            logger.exception(e)
            continue

    for u in extra_urls.strip().splitlines():
        filename = u.rsplit('/', 1)[-1]
        n, address = filename.removeprefix('Cjenik-Zabac-Food-Outlet-PJ-').removesuffix('.csv').split('-', 1)
        address = fix_address(address.replace('-', ' '))
        coll.append(Pricelist(u, address, 'Zagreb', zabac.id, f'PJ-{n}', datetime(2025, 5, 20), filename))

    if not coll:
        logger.warning('no zabac pricelists found!')
        return []

    logger.info(f'found {len(coll)} zabac pricelists')
    # TODO: filter by date
    # will be updated when zabac pricelists get less weird
    prod = []
    for t in coll:
        rows = get_csv_rows(ensure_archived(t, True))
        header = ';'.join(rows[0])
        for k in rows[1:]:
            if header == 'Artikl Šifra;Barcode;Pdv %;Naziv artikla / usluge;MPC':
                _id, barcode, vat, name, mpc = k
            elif header == 'Artikl;Pdv %;Naziv grupe artikla;Barcode;Naziv artikla / usluge;Mpc':
                _id, vat, category, barcode, name, mpc = k
            else:
                continue
            if '+' in barcode:  # scientific notation for barcode, really ?
                continue
            resolve_product(prod, barcode, zabac, t.location_id, name, mpc, None, None)

    return prod