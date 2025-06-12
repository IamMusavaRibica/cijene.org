import csv
import io
from pathlib import Path

import requests
from loguru import logger
from lxml.etree import HTML

from cijeneorg.fetchers.archiver import LocalArchiver, WaybackArchiver, Pricelist
from cijeneorg.models import ProductOffer, Product, Store
from cijeneorg.products import AllProducts
from cijeneorg.utils import most_occuring, remove_extra_spaces, fix_price

session = requests.Session()
session.headers.update({'User-Agent': 'cijene.org scraper (kontakt email: darac[at]ribica.dev)'})
ARCHIVE = Path('archive')
NotGiven = object()

def xpath(w: str | bytes, query: str, extra_headers = None, return_root: bool = False, verify: bool | str = True) -> list | tuple[list, HTML]:
    # NOTE: validators.url() is wrong for "https://www.ktc.hr/cjenici?poslovnica=SAMOPOSLUGA KOPRIVNICA PJ-88"
    if isinstance(w, str) and w.startswith('http'):
        w = session.get(w, headers=extra_headers or {}, verify=verify).text
    root = HTML(w)
    res = root.xpath(query)
    if return_root:
        return res, root
    return res


def ensure_archived(pricelist: Pricelist, return_it: bool = False, wayback: bool = True) -> bytes | None:
    # logger.debug(f'ensure_archived: {pricelist.url}')
    wayback and WaybackArchiver.archive(pricelist.url)
    return LocalArchiver.fetch(pricelist, return_it)


def get_csv_rows(raw: bytes) -> list[list[str]]:
    for enc in ('utf-8', 'cp1250'):
        try:
            raw_str = raw.decode(enc)
            break
        except UnicodeDecodeError:
            pass
    else:
        logger.warning(f'failed to find suitable encoding for CSV data!')
        return []
    delimiter = most_occuring(raw_str, ',', ';', '\t')
    with io.StringIO(raw_str) as stream:
        rows = list(csv.reader(stream, delimiter=delimiter))
    return rows

def resolve_product(coll: list, barcode: str, store: Store, location_id: str, name: str, price: float | str, quantity: float, may2_price: float | None) -> bool:
    barcode = barcode.lstrip('0')
    if barcode not in AllProducts:
        return False
    price = fix_price(price)
    may2_price = fix_price(may2_price)
    if not price and price != 0:
        return False
    name = (remove_extra_spaces(name)
            .removeprefix('--')  # Bakmaz
            .replace('0 ,5L', '0,5L')  # NTL ponekad
            )
    if not name:
        logger.warning(f'[{store.name}] product with {barcode = } has no name')
        return False
    product: Product
    product, qty = AllProducts[barcode]
    p = product.instance(store=store, store_location_id=location_id, offer_name=name, price=price, quantity=qty, may2_price=may2_price)
    coll.append(p)
    return True

def extract_offers_from_today(store: Store, plist: list[Pricelist], wayback: bool = False):
    if not plist:
        logger.warning(f'no {store.id} price lists found')
        return []
    logger.info(f'found {len(plist)} {store.id} prices')
    plist.sort(key=lambda x: x.dt, reverse=True)
    today = plist[0].dt.date()
    today_coll = []
    for p in plist:
        if p.dt.date() == today:
            today_coll.append(p)
        else:
            ensure_archived(p, wayback=wayback)
    return today_coll
