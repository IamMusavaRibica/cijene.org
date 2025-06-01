from linecache import cache

from loguru import logger
from lxml.etree import HTML

from cijenelib.fetchers.common import get_csv_rows, cached_fetch, resolve_product
from cijenelib.models import Store
from datetime import date, datetime
import requests

from cijenelib.utils import fix_address


def fetch_ktc_prices(ktc: Store):
    # https://www.ktc.hr/cjenici
    root0 = HTML(requests.get('https://www.ktc.hr/cjenici').content)
    hrefs = []
    for href0 in root0.xpath('//a[contains(@href, "cjenici?poslovnica")]/@href'):
        pricelist_url = 'https://www.ktc.hr/' + href0.removeprefix('/')
        store_id = href0.rsplit(maxsplit=1)[-1]
        root1 = HTML(requests.get(pricelist_url).content)
        for href1 in root1.xpath('//a[contains(@href, ".csv")]/@href'):
            full_url = 'https://www.ktc.hr/' + href1.removeprefix('/')
            filename = href1.rsplit('/', 1)[-1].removesuffix('.csv')
            market_type, full_addr, _storeid1, _id, _date, _time = filename.split('-')
            year, month, day = map(int, (_date[:4], _date[4:6], _date[6:8]))
            hour, minute, second = map(int, (_time[:2], _time[2:4], _time[4:6]))
            d = date(year, month, day)
            dt = datetime(year, month, day, hour, minute, second)

            # cities with two word names
            for t in {'GRUBISNO POLJE', 'MURSKO SREDISCE', 'VELIKA GORICA', 'DUGO SELO'}:
                if full_addr.endswith(t):
                    addr = full_addr[:-len(t)].strip()
                    city = t
                    break
            else:
                *a, city = full_addr.rsplit(maxsplit=1)
                addr = ' '.join(a).strip()
            addr = fix_address(addr)
            city = fix_city(city)
            hrefs.append((d, dt, full_url, store_id, addr, city))
            
    if not hrefs:
        logger.warning('no price lists found for KTC')
        return []

    hrefs.sort(reverse=True)
    today = hrefs[0][0]
    parsed_stores = set()
    prod = []
    for d, _, url, store_id, addr, city in hrefs:
        if d != today:
            break
        if store_id in parsed_stores:
            continue
        parsed_stores.add(store_id)
        if store_id not in ktc.locations:
            ktc.locations[store_id] = [city, None, addr, None, None, None]


        logger.debug(f'fetching KTC prices for {store_id} at {url}')
        rows = get_csv_rows(cached_fetch(url), delimiter=';', encoding='cp1250')
        for k in rows[1:]:
            # no 2.5.2025. price here
            name, _id, brand, _qty, units, mpc, ppu, barcode, category, last_30d_mpc, discount_mpc = k
            barcode = barcode.strip("'")
            if not barcode:
                continue
            price = float(discount_mpc) or float(mpc)
            # name = name.strip().replace('È', 'Č').replace('Æ', 'Ć') \
            #                    .replace('è', 'Č').replace('æ', 'Ć')  # uppercase Ć is intentional!

            # print([name, barcode, price])
            resolve_product(prod, barcode, ktc, store_id, name, price, None, None)


    return prod