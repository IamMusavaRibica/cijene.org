import os
import tomllib
from typing import Literal

from pydantic import BaseModel, field_validator, Field

from cijeneorg.stores import ALL_STORES


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
        toml = tomllib.load(f)
    # environment variables override the config
    if env_stores := os.getenv('CIJENEORG_STORES'):
        toml['stores'] = env_stores.lower().strip().split(',') if env_stores != 'all' else 'all'
    if env_days_back := os.getenv('CIJENEORG_DAYS_BACK'):
        toml['days_back'] = int(env_days_back)
    if env_stores_blacklist := os.getenv('CIJENEORG_STORES_BLACKLIST'):
        all_stores = [s.id for s in ALL_STORES]
        if toml['stores'] != 'all':
            all_stores = toml['stores']
        all_stores = set(all_stores)
        for blacklisted in env_stores_blacklist.lower().strip().split(','):
            all_stores.discard(blacklisted)
        toml['stores'] = list(all_stores)
        del all_stores

    return Config.model_validate(toml)
