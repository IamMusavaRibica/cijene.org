import re
import time
from datetime import datetime
from urllib.parse import urlencode

import requests
from loguru import logger

from cijenelib.fetchers._archiver import WaybackArchiver
from cijenelib.fetchers._common import get_csv_rows, resolve_product, xpath, ensure_archived, Pricelist
from cijenelib.models import Store
from cijenelib.utils import fix_address, fix_city, most_occuring, split_by_lengths


def fetch_boso_prices(boso: Store):
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
                else:            # supermarket-K.-P.-KRESIMIRA-IV-15-a-Vukovar-252413616.05.202507_42.csv
                    market_id, file_id, datetime0 = split_by_lengths(_rest, 4, 3)
                    datefmt = '%d.%m.%Y%H_%M.csv'
                    address = address.replace('-', ' ')

                if market_id.isdigit() and len(market_id) == 4:
                    url, = td_anchor.xpath('./a/@href')
                    dt = datetime.strptime(datetime0, datefmt)
                    coll.append(Pricelist(url, fix_address(address), fix_city(city), boso.id, market_id, dt, td_filename.text))
                else:
                    logger.warning(f'failed to parse store id from {td_filename.text}')

        except Exception as e:
            logger.warning(f'error {e!r} while fetching boso ajax {v}')
            logger.exception(e)
            continue

    if not coll:
        logger.warning('no boso prices found')
        return []
    logger.info(f'found {len(coll)} boso prices')
    coll.sort(key=lambda x: x.dt, reverse=True)
    today = coll[0].dt.date()
    today_coll = []
    for p in coll:
        if p.dt.date() == today:
            today_coll.append(p)
        else:
            ensure_archived(p, wayback=False)

    prod = []
    for t in today_coll:
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

            resolve_product(prod, barcode, boso, t.location_id, name, price, None, may2_price)
    return prod