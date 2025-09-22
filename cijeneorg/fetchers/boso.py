import re
import time
from datetime import datetime, date
from urllib.parse import urlencode

import requests
from loguru import logger

from cijeneorg.fetchers.archiver import WaybackArchiver
from cijeneorg.fetchers.common import get_csv_rows, resolve_product, xpath, ensure_archived, PriceList, \
    extract_offers_since
from cijeneorg.models import Store
from cijeneorg.utils import fix_address, fix_city, most_occuring, split_by_lengths


# Note: boso sometimes changes the price list csvs!
# See 'Uniques' https://web.archive.org/web/*/https://www.boso.hr/wp-content/uploads/cjenik/*
def fetch_boso_prices(boso: Store, min_date: date):
    WaybackArchiver.archive(index_url := 'https://www.boso.hr/cjenik/')
    html = requests.get(index_url).content
    if not (m := re.search(br'\{"ajax_url":"(.*?)","nonce":"(.*?)","version":"(.*?)"}', html)):
        logger.warning('failed to find ajax_url')
        return []

    ajax_url, nonce, version = map(lambda x: x.decode().replace('\\/', '/'), m.groups())
    coll = []
    for opt in xpath(html, '//select[@id="marketshop-filter"]/option[@value != ""]'):
        r = requests.post(ajax_url, data=urlencode({
            'action': 'filter_by_marketshop',
            'marketshop': (v := opt.get('value')),
            'nonce': nonce,
            '_': int(time.time() * 1000),
        }), headers={'content-type': 'application/x-www-form-urlencoded; charset=UTF-8'})
        try:
            r.raise_for_status()
            for tr in xpath(r.json()['data']['html'], '//tbody/tr'):
                # <tr><td>...</td><td>filename</td><td>dd.mm.yyyy</td><td><a href="file.csv" download="" class="download-button">Preuzmi</a></td></tr>
                _, td_filename, _, td_anchor = tr.getchildren()
                sep = most_occuring(td_filename.text, ', ', '-')
                pattern = r'(.+?){0}(.+){0}(.+?){0}(.+)'.format(sep)
                market_type, address, city, _rest = re.match(pattern, td_filename.text).groups()

                if sep == ', ':  # supermarket, K. P. KREŠIMIRA IV 15 a, Vukovar, 2524,137,17.05.2025,07_30.csv
                    market_id, file_id, datetime0 = _rest.split(',', 2)
                    datefmt = '%d.%m.%Y,%H_%M.csv'
                else:  # supermarket-K.-P.-KRESIMIRA-IV-15-a-Vukovar-252413616.05.202507_42.csv
                    market_id, file_id, datetime0 = split_by_lengths(_rest, 4, 3)
                    datefmt = '%d.%m.%Y%H_%M.csv'
                    address = address.replace('-', ' ')

                if market_id.isdigit() and len(market_id) == 4:
                    url, = td_anchor.xpath('./a/@href')
                    dt = datetime.strptime(datetime0, datefmt)
                    coll.append(
                        PriceList(url, fix_address(address), fix_city(city), boso.id, market_id, dt, td_filename.text))
                else:
                    logger.warning(f'failed to parse store id from {td_filename.text}')

        except Exception as e:
            logger.warning(f'error {e!r} while fetching boso ajax {v}')
            logger.exception(e)
            continue

    actual = extract_offers_since(boso, coll, min_date)

    prod = []
    for t in actual:
        rows = get_csv_rows(ensure_archived(t, True))
        for k in rows[1:]:
            *name, _id, brand, _qty, units, mpc, ppu, discount_mpc, last_30d_mpc, may2_price, barcode, category = k
            barcode = barcode.lstrip('0')
            if not barcode:
                continue

            price = float(discount_mpc or mpc)
            may2_price = float('0' + may2_price) or None  # po defaultu je nula

            name = ' '.join(name).strip().replace('Æ', 'ć')
            while '  ' in name:
                name = name.replace('  ', ' ')

            resolve_product(prod, barcode, boso, t.location_id, name, brand, price, None, may2_price, t.date)
    return prod
