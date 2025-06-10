from datetime import datetime
from urllib.parse import urlencode

from loguru import logger

from cijenelib.fetchers._archiver import WaybackArchiver, Pricelist
from cijenelib.fetchers._common import get_csv_rows, resolve_product, xpath, ensure_archived
from cijenelib.models import Store
from cijenelib.utils import fix_address, fix_city


def fetch_ntl_prices(ntl: Store):
    # comments in the HTML suggest that someone is working on it: https://ibb.co/Vdr4LT0
    WaybackArchiver.archive(index_url := 'https://www.ntl.hr/cjenici-za-ntl-supermarkete')

    # extract both today's hrefs and the archive hrefs and parse them in the same way
    hrefs, root0 = xpath(index_url, '//a[contains(@href, ".csv")]/@href', return_root=True)
    page_name ,= root0.xpath('//input[@name="pageName"]/@value')
    for opt in root0.xpath('//select[@name="archive_file_name"]/option[@value]/@value'):
        _url = index_url + '?' + urlencode({'pageName': page_name, 'archive_file_name': opt})
        WaybackArchiver.archive(_url)
        hrefs.extend(xpath(_url,'//a[contains(@href, ".csv")]/@href'))

    coll = []
    for href in hrefs:
        filename = href.rsplit('/', 1)[-1]
        market_type, address, city, location_id, file_id, rest = filename.split('_', 5)
        if not (location_id.isdigit() and len(location_id) == 5):
            print(f'failed to parse {filename}')
            continue
        dt = datetime.strptime(rest, '%d%m%Y_%H_%M_%S.csv')
        city = fix_city(city)
        address = fix_address(address).replace('Galoviaa', 'Galovića')
        coll.append(Pricelist(href, address, city, ntl.id, location_id, dt, filename))

    # for p in coll:
    #     print(p)

    if not coll:
        logger.warning(f'no prices found for ntl')
        return []

    logger.info(f'found {len(coll)} ntl pricelists')
    coll.sort(key=lambda x: x.dt, reverse=True)
    today = coll[0].dt.date()
    today_coll = []
    for p in coll:
        if p.dt.date() == today:
            today_coll.append(p)
        else:
            ensure_archived(p, wayback=False)

    prod = []
    for p in today_coll:
        rows = get_csv_rows(ensure_archived(p, True, wayback=False))
        for k in rows[1:]:
            name, _id, brand, _qty,  units, mpc, ppu, discount_mpc, last_30d_mpc, may2_price, barcode, category = k
            resolve_product(prod, barcode, ntl, p.location_id, name, discount_mpc or mpc, _qty, may2_price)

    return prod