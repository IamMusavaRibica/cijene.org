from datetime import datetime, date

import requests

from cijeneorg.fetchers.archiver import WaybackArchiver, PriceList
from cijeneorg.fetchers.common import extract_offers_since, ensure_archived
from cijeneorg.models import Store


def fetch_dm_prices(dm: Store, min_date: date):
    WaybackArchiver.archive('https://www.dm.hr/novo/promocije/nove-oznake-cijena-i-vazeci-cjenik-u-dm-u-2906632')
    api_url = 'https://content.services.dmtech.com/rootpage-dm-shop-hr-hr/novo/promocije/nove-oznake-cijena-i-vazeci-cjenik-u-dm-u-2906632?mrclx=false'
    url_prefix = 'https://content.services.dmtech.com/rootpage-dm-shop-hr-hr'

    json_data = requests.get(api_url).json()
    coll = []
    for item in json_data['mainData']:
        if item['type'] == 'CMDownload':
            full_url = url_prefix + item['data']['linkTarget']
            filename = full_url.rsplit('/', 1)[-1]

            # 11.6.2025_05.07.36
            _, date_str, time_str = item['data']['headline'].rsplit('_', 2)
            dt = datetime.strptime(date_str + '_' + time_str, '%d.%m.%Y_%H.%M.%S')
            coll.append(PriceList(full_url, '(sve prodavaonice)', None, dm.id, 'X', dt, filename))

    actual = extract_offers_since(dm, coll, min_date)

    prod = []
    for p in actual:
        raw_xlsx = ensure_archived(p, True, wayback=False)
        # TODO: implement parsing xlsx files!

    return prod
