import csv
import hashlib
import io
from datetime import datetime
from pathlib import Path

import requests
import validators
from loguru import logger
from lxml.etree import HTML

from cijenelib.fetchers._archiver import LocalArchiver, WaybackArchiver, Pricelist
from cijenelib.models import ProductOffer, Product, Store
from cijenelib.products import AllProducts
from cijenelib.utils import most_occuring, remove_extra_spaces, fix_price

session = requests.Session()
session.headers.update({'User-Agent': 'cijene.org scraper (kontakt email: darac[at]ribica.dev)'})
CACHE_DIR = Path('cached')
ARCHIVE = Path('archive')

def cached_fetch(url: str) -> bytes:
    checksum = hashlib.sha1(url.strip().encode()).hexdigest()
    filepath = CACHE_DIR / checksum
    if not filepath.exists():
        r = session.get(url)
        r.raise_for_status()
        filepath.write_bytes(r.content)
        return r.content
    return filepath.read_bytes()

def xpath(w: str | bytes, query: str, extra_headers = None):
    if isinstance(w, str) and validators.url(w):
        w = session.get(w, headers=extra_headers or {}).content
    root = HTML(w)
    return root.xpath(query)


def ensure_archived(pricelist: Pricelist, return_it: bool = False):
    WaybackArchiver.archive(pricelist.url)
    return LocalArchiver.fetch(pricelist, return_it)


def ensure_archived_file_data():
    ...

def get_csv_rows(raw: bytes, delimiter: str = None, encoding: str = None, transtable: dict = None) -> list[list[str]]:
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

def resolve_product(coll: list, barcode: str, store: Store, store_id: str, name: str, price: float | str, quantity: float, may2_price: float | None) -> bool:
    barcode = barcode.lstrip('0')
    if barcode not in AllProducts:
        return False
    price = fix_price(price)
    may2_price = fix_price(may2_price)
    if not price:
        return False
    name = remove_extra_spaces(name)
    name = name.removeprefix('--')  # Bakmaz
    if not name:
        logger.warning(f'[{store.name}] product with {barcode = } has no name')
        return False
    product: Product
    product, qty = AllProducts[barcode]
    p = product.instance(store=store, store_location_id=store_id, offer_name=name, price=price, quantity=qty, may2_price=may2_price)
    coll.append(p)
    return True


NotGiven = object()
def extract_offer_from_data(
        store: Store,
        *,
        product_name: str,      # naziv proizvoda
        product_id: str,        # sifra proizvoda koju valjda svaki proizvodac bira za sebe
        brand: str,
        net_quantity: float,      # neto kolicina
        units: str,             # jedinica mjere
        retail_price: str,      # maloprodajna cijena
        price_per_unit: str,    # cijena za jedinicu mjere
        barcode: str,
        category: str,

        # prema Odluci na https://narodne-novine.nn.hr/clanci/sluzbeni/full/2025_05_75_979.html
        # nije obavezno objaviti ovu cijenu na mrežnim stranicama!
        may2_price: float | None = NotGiven,
) -> ProductOffer | None:

    if may2_price == '' or may2_price is None:
        logger.warning(f'[{store.name}] product {product_name}, {barcode = } has no price on May 2nd 2025')
    elif may2_price is NotGiven:
        may2_price = None

    if not barcode:
        return



