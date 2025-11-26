import csv
import io
import os
from datetime import date, timedelta
from pathlib import Path

import requests
from loguru import logger
from lxml.etree import HTML

from cijeneorg.fetchers.archiver import LocalArchiver, WaybackArchiver, PriceList
from cijeneorg.models import Product, Store
from cijeneorg.products import AllProducts
from cijeneorg.utils import most_occuring, remove_extra_spaces, fix_price

session = requests.Session()
session.headers.update({'User-Agent': 'cijene.org scraper (kontakt email: darac[at]ribica.dev)'})
ARCHIVE = Path('archive')
NotGiven = object()


def xpath(w: str | bytes, query: str, extra_headers=None, return_root: bool = False,
          verify: bool | str = True) -> list | tuple[list, HTML]:
    # NOTE: validators.url() is wrong for "https://www.ktc.hr/cjenici?poslovnica=SAMOPOSLUGA KOPRIVNICA PJ-88"
    if isinstance(w, str) and w.startswith('http'):
        w = session.get(w, headers=extra_headers or {}, verify=verify).text
    root = HTML(w)
    res = root.xpath(query)
    if return_root:
        return res, root
    return res


def ensure_archived(pricelist: PriceList, return_it: bool = False, wayback: bool = True, force=False) -> bytes | None:
    # logger.debug(f'ensure_archived: {pricelist.url}')
    wayback and WaybackArchiver.archive(pricelist.url)
    if not return_it and (not force and os.getenv('DO_NOT_FILL_MY_DISK')) and pricelist.date < (date.today() - timedelta(days=2)):
        return
    return LocalArchiver.fetch(pricelist, return_it)


def get_csv_rows(raw: bytes) -> list[list[str]]:
    for enc in ('utf-8', 'cp1250'):
        try:
            raw_str = raw.decode(enc)
            break
        except UnicodeDecodeError:
            pass
    else:
        logger.error(f'failed to find suitable encoding for CSV data!')
        return []
    delimiter = most_occuring(raw_str, ',', ';', '\t')
    with io.StringIO(raw_str) as stream:
        rows = list(csv.reader(stream, delimiter=delimiter))
    return rows


def resolve_product(coll: list, barcode: str, store: Store, location_id: str, name: str, brand: str, price: float | str,
                    quantity: float, may2_price: float | None, offer_date: date) -> bool:
    barcode = barcode.strip().lstrip('0')
    if barcode not in AllProducts:
        nl = name.lower()
        for keyword in ('margarin', ):
            if keyword in nl:
                pass
                # logger.debug(f'Found new product! {store.id} {location_id}: {barcode}, {name}, {price=}, ')


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
    p = product.instance(barcode=barcode, date=offer_date, store=store, store_location_id=location_id, offer_name=name,
                         price=price, quantity=qty, may2_price=may2_price)
    coll.append(p)
    return True


def extract_offers_since(store: Store, pricelists: list[PriceList], min_date: date, wayback: bool = False,
                         wayback_past: bool = True) -> list[PriceList]:
    if not pricelists:
        logger.warning(f'no {store.id} price lists found')
        return []
    logger.info(f'found {len(pricelists)} {store.id} price lists')
    # logger.debug(f'wayback preference for {store.id}: {wayback = }, {wayback_past = }')
    pricelists.sort(key=lambda x: x.dt, reverse=True)
    selected = []
    for p in pricelists:
        if p.date >= min_date:
            selected.append(p)
        else:
            ensure_archived(p, wayback=wayback_past and wayback)
    return selected
