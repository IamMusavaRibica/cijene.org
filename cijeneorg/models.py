import enum
import math
from typing import TypeVar, Any, Callable

from pydantic import BaseModel, Field, model_validator

P = TypeVar('P', bound='ProductOffer')



class UnitType(enum.Enum):
    NONE = 0
    UNIT = 1

class Product(BaseModel):
    id: str
    name: str
    baseq: int | float = 1   # base quantity of units (some products are sold per 100 grams for example)
    unit: str = 'kom'
    unit_type: UnitType = UnitType.UNIT

    def __call__(self, **kwargs):
        return ProductOffer(product=self, **kwargs)

    def instance(self, **kwargs):
        return ProductOffer(product=self, **kwargs)

class Store(BaseModel):
    id: str
    name: str
    locations: dict[str, list]
    fetch_prices: Callable[['Store'], list['ProductOffer']]
    url: str | None = None
    google_maps_url: str | None = None

    @model_validator(mode='before')
    def preconstruct(cls, values):
        if values.get('id') is None:
            values['id'] = values['name'].lower().strip().replace(' ', '_')
        return values

    def fetch(self) -> list['ProductOffer']:
        return self.fetch_prices(self)

    def __call__(self, product: Product, quantity: int|float|None, **kwargs) -> 'ProductOffer':
        return ProductOffer(product=product, store=self, quantity=quantity, **kwargs)


class ProductOffer(BaseModel):
    product: Product
    offer_name: str | None = None
    price: float
    store: Store | str
    store_location_id: str
    may2_price: float | None  # sidrena cijena na 2.5.2025.
    quantity: int | float = 1
    url: str | None = None
    ogranicena_cijena: bool = False
    extra_data: dict[str, Any] = Field(default_factory=dict)

    @property
    def price_per_unit(self):
        return self.price / (self.quantity / self.product.baseq)

    @property
    def fmt_quantity(self) -> str:
        q = round(self.quantity, 2)
        if q == int(q):
            q = int(q)
        return str(q)

    @property
    def price_cmp_extra_class(self) -> str:
        if self.may2_price is None:
            return ''
        elif math.isclose(self.price, self.may2_price, rel_tol=0.00001):
            return ' equal'
        return ' better' if self.price < self.may2_price else ' worse'

class ProductOfferParsed(ProductOffer):
    store_ids: list
    store_location_datas: list[list] = Field(default_factory=list)
    tooltip_up: bool = False

    @property
    def locations_count(self) -> int:
        return len(self.store_location_datas)