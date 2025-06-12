from datetime import datetime

import requests.exceptions
from loguru import logger
from lxml.etree import XML

from cijeneorg.fetchers.archiver import WaybackArchiver, PriceList
from cijeneorg.fetchers.common import xpath, ensure_archived, resolve_product, extract_offers_from_today
from cijeneorg.models import Store


def fetch_vrutak_prices(vrutak: Store):
    WaybackArchiver.archive(index_url := 'https://www.vrutak.hr/cjenik-svih-artikala')
    coll = []
    for href in xpath(index_url, '//a[contains(@href, ".xml")]/@href'):
        filename = href.split('/')[-1]
        _, market_type, address, location_id, file_id, date_str = filename.split('-', 5)
        address = {
            'vodovodna20a': 'Vodovodna 20a',
            'samoborskacesta161a': 'Samoborska cesta 161a',
            'rabarova1a': 'Rabarova 1a',
            'bulvanova20': 'Ulica Slavoljuba Bulvana 20',
        }[address]
        dt = datetime.strptime(date_str, '%Y%m%d-%H%M%S.xml')
        coll.append(PriceList(href, address, 'Zagreb', vrutak.id, location_id, dt, filename))

    today_coll = extract_offers_from_today(vrutak, coll, wayback=True)

    prod = []
    for p in today_coll:
        try:
            xml_data = ensure_archived(p, True)
        except requests.exceptions.HTTPError as e:
            logger.warning(f'failed to fetch vrutak pricelist {p.url}: {e!r}')
            continue
        for item in XML(xml_data).findall('item'):
            name = item.findtext('naziv')
            mpc = item.findtext('mpcijena')
            barcode = item.findtext('barkod')
            _qty = item.findtext('nettokolicina')
            resolve_product(prod, barcode, vrutak, p.location_id, name, mpc, _qty, None)

    return prod