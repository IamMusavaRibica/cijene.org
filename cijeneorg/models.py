import datetime
import enum
from typing import TypeVar, Callable

from loguru import logger
from pydantic import BaseModel, Field, model_validator

P = TypeVar('P', bound='ProductOffer')
StoreLocationPredicate = Callable[['StoreLocation'], bool]

class UnitType(enum.Enum):
    NONE = 0
    UNIT = 1


class Product(BaseModel):
    id: str
    name: str
    baseq: int | float = 1  # base quantity of units (some products are sold per 100 grams for example)
    unit: str = 'kom'
    unit_type: UnitType = UnitType.UNIT

    def __call__(self, **kwargs):
        return ProductOffer(product=self, **kwargs)

    def instance(self, **kwargs):
        return ProductOffer(product=self, **kwargs)


class StoreLocation(BaseModel):
    store: 'Store' = Field(exclude=True)
    location_id: str
    city: str
    address: str
    lat: float
    lng: float
    google_maps_url: str | None


class Store(BaseModel):
    id: str
    name: str
    locations: dict[str, StoreLocation] = Field(default_factory=dict)
    fetch_prices: Callable[..., list['ProductOffer']] = Field(exclude=True)
    url: str

    @model_validator(mode='before')
    def preconstruct(cls, values):
        if not isinstance(values, dict):
            raise ValueError(f'expected dict, got {type(values)}')
        if values.get('id') is None:
            values['id'] = values['name'].lower().strip().replace(' ', '_')
        return values

    def fetch(self, *, min_date: datetime.date | None = None) -> list['ProductOffer']:
        return self.fetch_prices(self, min_date=min_date)

    def register_location(self, location_id: str, city: str, address: str, lat: float, lng: float, google_maps_url: str):
        if location_id in self.locations:
            logger.warning(f'Overwriting existing location {location_id} in store {self.id}')
        self.locations[location_id] = StoreLocation(
            store=self, location_id=location_id, city=city, address=address,
            lat=lat, lng=lng, google_maps_url=google_maps_url
        )


class ProductOffer(BaseModel):
    product: Product
    barcode: str
    offer_name: str | None = None
    price: float
    store: Store | str
    store_location_id: str
    may2_price: float | None  # sidrena cijena na 2.5.2025.
    quantity: int | float = 1
    date: datetime.date

    @property
    def price_per_unit(self):
        return self.price / (self.quantity / self.product.baseq)

    @property
    def fmt_quantity(self) -> str:
        q = round(self.quantity, 2)
        if q == int(q):
            q = int(q)
        return str(q)

    # @property
    # def price_cmp_extra_class(self) -> str:
    #     if self.may2_price is None:
    #         return ''
    #     elif math.isclose(self.price, self.may2_price, rel_tol=0.00001):
    #         return ' equal'
    #     return ' better' if self.price < self.may2_price else ' worse'


# Deprecated!
class ProductOfferParsed(ProductOffer):
    store_ids: list
    store_location_datas: list[list] = Field(default_factory=list)
    tooltip_up: bool = False

    @property
    def locations_count(self) -> int:
        return len(self.store_location_datas)
