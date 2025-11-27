# https://cijene.org/

<!--
Projekt za arhiviranje, pretraživanje i prikaz cijena prema [Odluci NN 75/2025](https://narodne-novine.nn.hr/clanci/sluzbeni/2025_05_75_979.html). **WORK IN PROGRESS!**  

Nadam se da će kod nekome biti koristan za svoje istraživanje. Ovaj repository objavljen je pod AGPL-3.0 licencom. Molim vas da date adekvatan credit (npr. [poveznica](https://github.com/IamMusavaRibica/cijene.org/)) tamo gdje je potrebno. Ako imate neke komentare ili prijedloge, otvorite prvo issue pa ćemo diskutirati

**Također pogledajte: https://github.com/senko/cijene-api**
-->

## ~ Development branch ~
- korištenje PostgreSQL baze podataka umjesto SQLite
- razdvajanje webservera i fetchera (scrapera) u zasebne procese u docker composeu

Upute za običnu instalaciju za development:
1. Install PostgreSQL
2. Dodaj `C:\Program Files\PostgreSQL\18\bin` na PATH
3. Spojiti se u postgres `psql -U postgres` pa zalijepit ovo:
```sql
CREATE ROLE cijene_admin   WITH LOGIN PASSWORD 'secure-pw-changeme' NOSUPERUSER CREATEDB CREATEROLE;
CREATE ROLE cijene_fetcher WITH LOGIN PASSWORD 'secure-pw-changeme' NOSUPERUSER NOCREATEDB NOCREATEROLE;
CREATE ROLE cijene_web     WITH LOGIN PASSWORD 'secure-pw-changeme' NOSUPERUSER NOCREATEDB NOCREATEROLE;

CREATE DATABASE cijene;
       
``` 
4. Prebacite se na novu bazu naredbom `\c cijene` ili `quit` iz sesije kao postgres pa se spojiti ovako: `psql -U cijene_admin -d cijene`
5. Pokrenut ovo:
```sql
CREATE TABLE IF NOT EXISTS map_product_id (
    id          INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    product_key TEXT NOT NULL UNIQUE
);
CREATE TABLE IF NOT EXISTS map_barcode (
    id          INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    barcode_key TEXT NOT NULL UNIQUE
);
CREATE TABLE IF NOT EXISTS map_store_id (
    id          INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    store_key   TEXT NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS product_offers (
    id                  BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    product_id          INTEGER NOT NULL    REFERENCES map_product_id(id) ON DELETE RESTRICT,
    barcode_id          INTEGER             REFERENCES map_barcode(id) ON DELETE SET NULL,
    store_id            INTEGER NOT NULL    REFERENCES map_store_id(id) ON DELETE RESTRICT,
    product_name        TEXT NOT NULL,       -- store's name for this product
    price               INTEGER NOT NULL,    -- price in cents
    store_location_id   TEXT NOT NULL,       -- not mapped
    price_25            INTEGER,             -- price on 2.5.2025. optional
    yyyymmdd            INTEGER NOT NULL,    -- date as integer e.g. 20251127
    quantity            DOUBLE PRECISION NOT NULL,  -- quantity (float)
    fetched_at          TIMESTAMPTZ DEFAULT now()   -- when this row was fetched
);

CREATE INDEX IF NOT EXISTS idx_product_offers_product_id ON product_offers (product_id);
CREATE INDEX IF NOT EXISTS idx_product_offers_barcode_id ON product_offers (barcode_id);
CREATE INDEX IF NOT EXISTS idx_product_offers_store_id ON product_offers (store_id);
CREATE INDEX IF NOT EXISTS idx_product_offers_yyyymmdd ON product_offers (yyyymmdd);
CREATE INDEX IF NOT EXISTS idx_product_offers_product_yyyymmdd ON product_offers (product_id, yyyymmdd DESC);




GRANT CONNECT ON DATABASE cijene TO cijene_fetcher, cijene_web;
GRANT USAGE   ON SCHEMA public   TO cijene_fetcher, cijene_web;

GRANT INSERT, SELECT ON TABLE product_offers, map_product_id, map_barcode, map_store_id TO cijene_fetcher;
GRANT INSERT, SELECT ON TABLE product_offers, map_product_id, map_barcode, map_store_id TO cijene_web;

```




## AI disclaimer

Ovaj kod je djelomično generiran korištenjem pomoću umjetne inteligecije, uglavnom za dizajn i funkcionalnost stranice
(HTML i JavaScript). Popis pojedinih trgovina i proizvoda u potpunosti je odrađen ručno.