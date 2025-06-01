import concurrent.futures
import traceback
from collections import defaultdict

from loguru import logger

from cijenelib.models import Product, ProductOffer, ProductOfferParsed
from cijenelib.stores import *


class ProductApi:
    def __init__(self, stores):
        self._stores: list[Store] = stores
        self._products: dict[str, Product] = {}
        self._offers_by_store: dict[str, list[ProductOffer]] = defaultdict(list)
        self._offers_by_product: dict[str, list[ProductOffer]] = defaultdict(list)

    def update_prices(self):
        with concurrent.futures.ThreadPoolExecutor(max_workers=10, thread_name_prefix='PriceFetcherThread') as executor:
            futures = {executor.submit(store.fetch_prices, store): store for store in self._stores}
            for fut in concurrent.futures.as_completed(futures):
                try:
                    offers = fut.result()
                except Exception as e:
                    logger.error(f'Error while fetching prices: {e}')
                    traceback.print_exc()
                else:
                    if not isinstance(offers, list):
                        logger.error(f'Expected list of offers, got {type(offers)}')
                        continue
                    store = futures[fut]
                    logger.info(f'Fetched {len(offers)} offers from {store.name}')
                    self.add_offers_from_store(store, offers)


    def add_product(self, product: Product):
        self._products[product.id] = product

    @property
    def products_by_id(self):
        return self._products

    def get_product_by_id(self, product_id: str) -> Product:
        return self._products.get(product_id)

    def get_offers_by_product(self, product: Product) -> list[ProductOfferParsed]:
        have: dict[tuple, ProductOfferParsed] = {}
        raw_offers = self._offers_by_product.get(product.id, [])
        offers = []
        for o in raw_offers:
            key = (o.offer_name, o.store.id, str(round(o.price, 2)))
            value = have.get(key)
            if value is None:
                _old = o.model_dump()
                value = have[key] = ProductOfferParsed.model_validate({**_old, 'store_ids': []})
                offers.append(value)
            value.store_ids.append(o.store_location_id)
        for new_o in offers:
            l = []
            for store_id in new_o.store_ids:
                store_loc_data = new_o.store.locations.get(store_id)
                if store_loc_data is not None:
                    l.append(store_loc_data + [store_id])
            new_o.store_location_datas = l

        offers.sort(key=lambda x: x.price_per_unit)
        howmuch = 0
        if len(offers) > 15: howmuch = 9
        elif len(offers) > 7: howmuch = 4
        if howmuch:
            for new_o in offers[-howmuch:]:
                new_o.tooltip_up = True
        return offers

    def add_offers_from_store(self, store: Store, offers: list[ProductOffer]):
        for o in offers:
            if o.product.id not in self._products:
                self._products[o.product.id] = o.product
        previous = self._offers_by_store.get(store.id)
        if previous:
            ...
        self._offers_by_store[store.id].clear()
        self._offers_by_store[store.id].extend(offers)
        self._update_offers_by_product()

    def _update_offers_by_product(self):
        new_dict = defaultdict(list)
        for offers in self._offers_by_store.values():
            for offer in offers:
                new_dict[offer.product.id].append(offer)
        self._offers_by_product = new_dict


def demo():
    provider = ProductApi(stores=[Konzum, Spar, Tommy, Studenac, Ribola, Lidl, Plodine, Kaufland, Eurospin, Metro,
                                  Boso, NTL, KTC, TrgovinaKrk])
    # provider = ProductApi(stores=[])
    provider.update_prices()
    return provider


# Provider = ProductApi()
# Provider.add_product(CocaCola_1L)
# Provider.add_product(Jabuka)
# Provider.add_product(Mrkva)
# Provider.add_product(Sampon)
# Provider.add_product(Tjestenina)
# Provider.add_product(Pasteta)
# Provider.add_product(Kajzerica)
