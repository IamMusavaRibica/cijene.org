import os

from cijeneorg.config import load_config

cfg = load_config()

print('Fetcher works!')
print('stores:', cfg.stores)
print('days_back:', cfg.days_back)
print(os.environ['DBCONNSTRING'])
