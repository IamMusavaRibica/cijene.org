import sqlite3
import threading
import time
from contextlib import contextmanager
from datetime import date, timedelta
from pathlib import Path

import urllib3.exceptions
from loguru import logger

from cijeneorg.config import Config
from cijeneorg.models import Product, ProductOffer, Store, StoreLocationPredicate
from cijeneorg.stores import ALL_STORES, ALL_STORES_BY_ID


# noinspection SqlNoDataSourceInspection
class ProductApi:
    def __init__(self, stores, days_back: int = 0):
        self._stores: list[Store] = stores
        self._products: dict[str, Product] = {}
        self._updater_thread = None

        self._db_path = Path('data/cijene.sqlite3')
        self._db_ready = False
        self._days_back = days_back

    _SCHEMA_SQL = """
    CREATE TABLE IF NOT EXISTS product_offers (
      product_id         TEXT NOT NULL,
      product_barcode    TEXT NOT NULL,
      product_name       TEXT NOT NULL,
      price_cents        INTEGER NOT NULL,
      store_id           TEXT NOT NULL,
      store_location_id  TEXT NOT NULL,
      may2_price_cents   INTEGER,          -- NULL if unknown
      quantity           REAL NOT NULL,    -- e.g. 1, 0.5, etc.
      date_yyyymmdd      INTEGER NOT NULL, -- e.g. 20250826
      UNIQUE (product_id, product_barcode, store_id, store_location_id, date_yyyymmdd)
    );
    CREATE INDEX IF NOT EXISTS idx_offers_product_date
      ON product_offers (product_id, date_yyyymmdd);
    CREATE INDEX IF NOT EXISTS idx_offers_barcode_date
      ON product_offers (product_barcode, date_yyyymmdd);
    CREATE INDEX IF NOT EXISTS idx_offers_store_date
      ON product_offers (store_id, date_yyyymmdd);
    CREATE INDEX IF NOT EXISTS idx_offers_location_date
      ON product_offers (store_location_id, date_yyyymmdd);
    """

    _UPSERT_SQL = (
        "INSERT INTO product_offers ("
        "  product_id, product_barcode, product_name, price_cents, store_id, store_location_id, "
        "  may2_price_cents, quantity, date_yyyymmdd"
        ") VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?) "
        "ON CONFLICT(product_id, product_barcode, store_id, store_location_id, date_yyyymmdd) DO UPDATE SET "
        "  product_name=excluded.product_name, "
        "  price_cents=excluded.price_cents, "
        "  may2_price_cents=excluded.may2_price_cents, "
        "  quantity=excluded.quantity"
    )

    def _conn(self, readonly: bool = False) -> sqlite3.Connection:
        # one connection per call; safe across threads.
        self._db_path.parent.mkdir(parents=True, exist_ok=True)
        if readonly:
            uri = f"file:{self._db_path}?mode=ro"
            conn = sqlite3.connect(uri, uri=True, isolation_level=None, timeout=30.0)
        else:
            conn = sqlite3.connect(self._db_path, isolation_level=None, timeout=30.0)
        conn.execute("PRAGMA journal_mode=WAL;")
        conn.execute("PRAGMA synchronous=NORMAL;")
        conn.execute("PRAGMA foreign_keys=ON;")
        conn.row_factory = sqlite3.Row
        return conn

    @contextmanager
    def _connect(self, readonly: bool = False):
        """
        Yields a SQLite connection and guarantees clean close.
        For writes, it also ensures the schema exists.
        """
        conn = None
        try:
            conn = self._conn(readonly=readonly)
            if not readonly:
                self._ensure_db(conn)
            yield conn
        finally:
            if conn is not None:
                try:
                    conn.close()
                except Exception:
                    pass

    def _ensure_db(self, conn: sqlite3.Connection) -> None:
        if not self._db_ready:
            conn.executescript(self._SCHEMA_SQL)
            self._db_ready = True

    @staticmethod
    def _yyyymmdd(d: date) -> int:
        return int(d.strftime("%Y%m%d"))

    @staticmethod
    def _from_yyyymmdd(v: int) -> date:
        y = v // 10000
        m = (v // 100) % 100
        d = v % 100
        return date(y, m, d)

    def _upsert_offers(self, conn: sqlite3.Connection, offers: list[ProductOffer]) -> None:
        """Persist today's offers. Assumes _UPSERT_SQL includes product_barcode."""
        rows: list[tuple] = []

        for o in offers:
            # store_id can be a Store or already a string in some fetchers
            if isinstance(o.store, str):
                logger.warning(f'store_id is str: {o.store}')
            store_id = o.store.id if hasattr(o.store, "id") else str(o.store)

            # cents (round to nearest) and nullable May 2 price
            price_cents = int(round(o.price * 100))
            may2_cents = None if (o.may2_price is None) else int(round(o.may2_price * 100))

            # quantity defaults to 1 if None/falsey; store as float
            qty = float(o.quantity or 1)
            day = int(o.date.strftime("%Y%m%d"))

            # normalize barcode a bit; fall back to product_id if somehow missing
            barcode = (o.barcode or o.product.id).strip().lstrip("0") or o.product.id

            rows.append((
                o.product.id,  # product_id (group)
                barcode,  # product_barcode (variant)
                o.offer_name,  # product_name
                price_cents,  # price_cents
                store_id,  # store_id
                o.store_location_id,  # store_location_id
                may2_cents,  # may2_price_cents (nullable)
                qty,  # quantity
                day,  # date_yyyymmdd
            ))

        if rows:
            conn.executemany(self._UPSERT_SQL, rows)

    def update_prices(self):
        def work():
            _start = time.perf_counter()
            min_date = date.today() - timedelta(days=self._days_back)

            for store in self._stores:
                logger.info(f'started fetching {store.id} prices')
                try:
                    offers = store.fetch(min_date=min_date)
                except (urllib3.exceptions.HTTPError, urllib3.exceptions.ProtocolError) as e:
                    logger.error(f'network error while fetching {store.id} prices: {e!r}')
                except Exception as e:
                    logger.error(f'unknown error while fetching {store.id} prices: {e!r}')
                    logger.exception(e)
                else:
                    logger.info(f'fetched {len(offers)} offers from {store.name}')
                    self.add_offers_from_store(store, offers)
            logger.info(f'finished updating prices, took {time.perf_counter() - _start:.3f} s')

        self._updater_thread = threading.Thread(target=work, name='PriceFetcherThread', daemon=True)
        self._updater_thread.start()

        # with concurrent.futures.ThreadPoolExecutor(max_workers=10, thread_name_prefix='PriceFetcherThread') as executor:
        #     futures = {executor.submit(store.fetch_prices, store): store for store in self._stores}
        #     for fut in concurrent.futures.as_completed(futures):
        #         store = futures[fut]
        #         try:
        #             offers = fut.result()
        #         except Exception as e:
        #             logger.error(f'Error while fetching {store.id} prices: {e}')
        #             traceback.print_exc()
        #         else:
        #             if not isinstance(offers, list):
        #                 logger.error(f'Expected list of offers, got {type(offers)}')
        #                 continue
        #             logger.info(f'Fetched {len(offers)} offers from {store.name}')
        #             self.add_offers_from_store(store, offers)

    def add_product(self, product: Product):
        if product.id in self._products:
            logger.warning(f'duplicate product {product.id} ({product.name}), overwriting')
        self._products[product.id] = product

    @property
    def products_by_id(self):
        return self._products

    def get_product_by_id(self, product_id: str) -> Product:
        return self._products.get(product_id)

    def get_offers_by_product(
            self,
            product: Product,
            on_date: date | None = None,
            predicate: StoreLocationPredicate = lambda s: True
    ) -> list[ProductOffer]:
        """
        Return offers only for 'today' defined as the latest day present in SQLite
        for this product_id. No in-memory dictionaries involved.
        """
        date_int = on_date and self._yyyymmdd(on_date)
        if date_int is None:
            date_int = self._latest_date_for_product(product.id)
        if date_int is None:
            return []

        logger.debug(f'latest date is: {date_int}')

        # map store_id -> Store so templates keep working
        # store_map: dict[str, Store] = {s.id: s for s in self._stores}   <-- this is a mayhem
        store_map = ALL_STORES_BY_ID

        with self._connect(True) as conn:
            cur = conn.execute(
                "SELECT product_name, price_cents, store_id, store_location_id, "
                "       may2_price_cents, quantity, date_yyyymmdd, product_barcode "
                "FROM product_offers "
                "WHERE product_id=? AND date_yyyymmdd=? "
                "ORDER BY (price_cents * 1.0) ASC",
                (product.id, date_int),
            )
            rows = cur.fetchall()

        offers: list[ProductOffer] = []
        for r in rows:
            store_obj = store_map.get(r["store_id"])
            if store_obj is None:
                logger.warning(f'unknown store {r["store_id"]}')
            assert isinstance(store_obj, Store)
            store_location = store_obj.locations.get(r["store_location_id"])
            if store_location is None:
                ...
            elif predicate(store_location) is True:
                offers.append(ProductOffer(
                    product=product,
                    offer_name=r["product_name"],
                    price=(r["price_cents"] / 100.0),
                    store=store_obj,
                    store_location_id=r["store_location_id"],
                    may2_price=None if r["may2_price_cents"] is None else (r["may2_price_cents"] / 100.0),
                    quantity=float(r["quantity"]),
                    barcode=r["product_barcode"],
                    date=self._from_yyyymmdd(int(r["date_yyyymmdd"])),
                ))

        # keep your original ordering logic
        try:
            offers.sort(key=lambda x: x.price_per_unit)
        except Exception:
            offers.sort(key=lambda x: x.price)

        return offers

    def get_offers_by_product_grouped(
            self,
            product: Product,
            on_date: date | None = None,
            predicate: StoreLocationPredicate = lambda s: True
    ) -> list[ProductOffer]:
        raw_offers = self.get_offers_by_product(product, on_date, predicate)
        GroupKey = tuple[str, str, int]  # (store_id, barcode, price_cents)
        # TODO: offer_name or barcode?
        grouped: dict[GroupKey, dict] = {}
        for raw in raw_offers:
            key = (raw.store.id, raw.barcode, int(raw.price * 100))
            if g := grouped.get(key):
                g['count'] += 1
            else:
                grouped[key] = {'offer': raw, 'count': 1}

        return [i['offer'] for i in grouped.values()]

    def add_offers_from_store(self, store: Store, offers: list[ProductOffer]):
        for o in offers:
            if o.product.id not in self._products:
                self._products[o.product.id] = o.product

        with self._connect(False) as conn:
            self._upsert_offers(conn, offers)

    def _latest_date_for_product(self, product_id: str) -> int | None:
        """Return MAX(date_yyyymmdd) we have in SQLite for the given product_id."""
        with self._connect(True) as conn:
            cur = conn.execute(
                "SELECT MAX(date_yyyymmdd) AS d FROM product_offers WHERE product_id=?",
                (product_id,),
            )
            row = cur.fetchone()
            return int(row["d"]) if row and row["d"] is not None else None


def get_provider(cfg: Config) -> ProductApi:
    provider = ProductApi(stores=[s for s in ALL_STORES if cfg.should_fetch(s.id)], days_back=cfg.days_back)
    provider.update_prices()
    return provider
