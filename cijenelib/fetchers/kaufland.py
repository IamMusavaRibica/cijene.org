import json
import re
from datetime import date
from random import randint

from loguru import logger

from cijenelib.fetchers._common import get_csv_rows, cached_fetch, resolve_product
from cijenelib.models import Store
from lxml.etree import HTML, tostring
import requests

from cijenelib.utils import fix_city

BASE_URL = 'https://www.kaufland.hr'
def fetch_kaufland_prices(kaufland: Store):
    root0 = HTML(requests.get(BASE_URL + '/akcije-novosti/popis-mpc.html').content)
    x ,= root0.xpath('//div[contains(@data-props, "/akcije-novosti/popis-mpc")]/@data-props')
    data_url = BASE_URL + json.loads(x)['settings']['dataUrlAssets']

    logger.debug('kaufland index url: {}', data_url)
    files = requests.get(data_url).json()

    hrefs = []
    # whoever decided how to name these files is on hard drugs
    for f in files:
        filename = f['label']
        url = BASE_URL + f['path']


        match0 = list(re.finditer(r'(\d{1,2})_(\d{1,2})_(20\d{2})', filename)) \
              or list(re.finditer(r'([0123]\d)([01]\d)(20\d\d)', filename))
        if match0:
            m = match0[0]
            day, month, year = map(int, m.groups())
            dd = date(year, month, day)
            hrefs.append((dd, url, filename[:m.start()-1]))
        else:
            logger.warning(f'unknown date format in filename (failed to parse?) {filename}')

    if not hrefs:
        logger.warning(f'no valid kaufland files found!')
        return []

    hrefs.sort(reverse=True)
    today = hrefs[0][0]
    prod = []
    for d, url, filename in hrefs:
        if d != today:
            break
        # logger.debug(f'fetching kaufland prices for from {filename}')
        market_type, *full_addr, store_id = filename.split('_')
        full_addr = ' '.join(full_addr).replace('  ', ' ').strip()
        for t in {'Slavonski Brod', 'Nova Gradiska', 'Nova Gradiška', 'Velika Gorica', 'Dugo Selo'}:
            if full_addr.endswith(t):
                addr = full_addr[:-len(t)].strip()
                city = t
                break
        else:
            *a, city = full_addr.rsplit(maxsplit=1)
            addr = ' '.join(a).strip()

        city = fix_city(city)
        if store_id not in kaufland.locations:
            kaufland.locations[store_id] = [city, None, addr, None, None, None]

        raw = cached_fetch(url)
        for enc in ('utf8', 'cp1250'):  # some are utf8, some are cp1250 as of june 2nd/3rd
            try:
                rows = get_csv_rows(raw, delimiter='\t', encoding=enc)
            except:
                pass
            else:
                # logger.info(f'guessed encoding {enc} for {url}')
                break
        else:
            import time
            filename = f'kaufland_{int(time.time())}_{randint(1, 1000)}.bin'
            logger.error(f'failed to decode kaufland prices, saved to {filename}')
            with open(f'cached/{filename}', 'wb') as f:
                f.write(raw)
            continue

        for k in rows[1:]:
            name, _id, brand, net_qty, units, mpc, is_sale, u, units, ppu, discount_mpc, last_30d_mpc, may2_price, barcode, category = k
            if not barcode:
                continue

            quantity = float(net_qty.replace(',', '.'))
            price = mpc or discount_mpc
            if not price:
                # logger.warning(f'product {name}, {barcode =} has no price, {url}')
                continue
            price = float(price.replace(',', '.'))
            try:
                may2_price = float(may2_price.removeprefix('MPC 2.5.2025=').removesuffix('€').replace(',', '.'))
            except ValueError:
                may2_price = None

            resolve_product(prod, barcode, kaufland, store_id, name, price, quantity, may2_price)

    return prod