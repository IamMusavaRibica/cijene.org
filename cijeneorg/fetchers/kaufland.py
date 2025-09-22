import json
import re
from datetime import datetime, date

import requests
from loguru import logger

from cijeneorg.fetchers.archiver import PriceList, WaybackArchiver
from cijeneorg.fetchers.common import get_csv_rows, resolve_product, xpath, ensure_archived, extract_offers_since
from cijeneorg.models import Store
from cijeneorg.utils import fix_city, split_by_lengths

HOST = 'https://www.kaufland.hr'


def fetch_kaufland_prices(kaufland: Store, min_date: date):
    WaybackArchiver.archive(index_url := 'https://www.kaufland.hr/akcije-novosti/popis-mpc.html')
    x, = xpath(index_url, '//div[contains(@data-props, "/akcije-novosti/popis-mpc")]/@data-props')
    data_url = HOST + json.loads(x)['settings']['dataUrlAssets']
    files = requests.get(data_url).json()

    # whoever decided how to name these files is on hard drugs
    coll = []
    for f in files:
        filename = f['label']
        url = HOST + f['path']
        match_ = list(re.finditer(r'(\d{1,2})_(\d{1,2})_(20\d{2})', filename)) \
                 or list(re.finditer(r'([0123]\d)([01]\d)(20\d\d)', filename))
        if match_:
            m = match_[0]
            day, month, year = map(int, m.groups())
            dt = datetime(year, month, day)
            p1, _ = split_by_lengths(filename, m.start() - 1)
            market_type, *full_addr, location_id = p1.split('_')
            full_addr = ' '.join(full_addr).replace('  ', ' ').strip()
            for t in {'Slavonski Brod', 'Nova Gradiska', 'Nova Gradiška', 'Velika Gorica', 'Dugo Selo'}:
                if full_addr.endswith(t):
                    address = full_addr[:-len(t)].strip()
                    city = t
                    break
            else:
                *a, city = full_addr.rsplit(maxsplit=1)
                address = ' '.join(a).strip()
            city = fix_city(city)
            coll.append(PriceList(url, address, city, kaufland.id, location_id, dt, filename))

        else:
            logger.warning(f'failed to parse kaufland pricelist {filename}')

    actual = extract_offers_since(kaufland, coll, min_date)

    prod = []
    for p in actual:
        rows = get_csv_rows(ensure_archived(p, True))
        for k in rows[1:]:
            name, _id, brand, _qty, units, mpc, is_sale, u, units, ppu, discount_mpc, last_30d_mpc, may2_price, barcode, category = k
            # may2_price = may2_price.removeprefix('MPC 2.5.2025=').removesuffix('€')
            # TODO: kaufland has `MPC 21.5.2025=3,89` somewhere
            may2_price = may2_price.rsplit('=')[-1].removesuffix('€')
            resolve_product(prod, barcode, kaufland, p.location_id, name, brand, discount_mpc or mpc, _qty, may2_price, p.date)

    return prod
