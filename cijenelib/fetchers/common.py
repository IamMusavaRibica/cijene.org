from pathlib import Path
from typing import Optional

import requests
import hashlib
import io
import csv

from loguru import logger

from cijenelib.models import ProductOffer, Product, Store
from cijenelib.products import AllProducts

CACHE_DIR = Path('cached')
def cached_fetch(url: str) -> bytes:
    checksum = hashlib.sha1(url.strip().encode()).hexdigest()
    filepath = CACHE_DIR / checksum
    if not filepath.exists():
        r = requests.get(url, headers={'User-Agent': 'cijene.org scraper (kontakt email: darac[at]ribica.dev)'})
        r.raise_for_status()
        filepath.write_bytes(r.content)
        return r.content
    return filepath.read_bytes()

def get_csv_rows(raw: bytes, delimiter: str, encoding: str, transtable: dict = None) -> list[list[str]]:
    rawstr = raw.decode(encoding)
    if transtable:
        rawstr = rawstr.translate(transtable)
    with io.StringIO(rawstr) as stream:
        rows = list(csv.reader(stream, delimiter=delimiter))
    return rows

def resolve_product(coll: list, barcode: str, store: Store, store_id: str, name: str, price: float, quantity: float, may2_price: float | None) -> bool:
    barcode = barcode.lstrip('0')
    if barcode not in AllProducts:
        return False
    while '  ' in name:
        name = name.replace('  ', ' ')
    name = name.strip()
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



