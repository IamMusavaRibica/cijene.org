import tomllib
from pydantic import BaseModel, field_validator, Field
from typing import Literal

class Config(BaseModel):
    stores: Literal['all'] | list[str] = 'all'
    days_back: int = Field(0, ge=0)  # nonnegative integer

    # noinspection PyNestedDecorators
    @field_validator('stores', mode='before')
    @classmethod
    def validate_stores(cls, v):
        if isinstance(v, str) and v.strip() == 'all':
            return 'all'
        if isinstance(v, list):
            return [str(i).strip().casefold() for i in v]
        raise TypeError('stores must be "all" or a list of store IDs')

    def should_fetch(self, store_id: str) -> bool:
        return self.stores == 'all' or store_id.casefold() in self.stores


def load_config(path: str = 'cijene.toml') -> Config:
    with open(path, 'rb') as f:
        return Config.model_validate(tomllib.load(f))
