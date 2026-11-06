from datetime import datetime, date

from cijeneorg.fetchers.archiver import WaybackArchiver, PriceList
from cijeneorg.fetchers.common import xpath, ensure_archived, extract_offers_since, get_csv_rows, resolve_product
from cijeneorg.models import Store

from loguru import logger


def fetch_tobylex_prices(tobylex: Store, min_date: date):
    # https://tobylex.net/testna-stranica/
    # adresa je Froudeova 34, 10020 Zagreb, ali je virtualna trgovina
    WaybackArchiver.archive(index_url := 'https://tobylex.net/cjenik/')
    coll = []

    # novi format: webshop_tobylex.net_POS1_000085_06.11.2026_07-30-02.csv
    formats = ['cjenik_%Y%m%d_%H%M%S', 'cjenik-%Y-%m-%d', '%d.%m.%Y_%H-%M-%S']

    def get_dt_format(filename, suffix):
        for candidate in (filename, '_'.join(filename.split('_')[-2:])):
            for fmt in formats:
                try:
                    return datetime.strptime(candidate, fmt + suffix)
                except ValueError:
                    pass
        logger.error(f'Could not parse filename {filename}')

    for xml_href in xpath(index_url, '//a[contains(@href, ".xml")]/@href'):
        filename = xml_href.rsplit('/', 1)[-1]
        dt = get_dt_format(filename, '.xml')
        if dt is not None:
            ensure_archived(PriceList(xml_href, '(internet trgovina)', '', tobylex.id, 'WEBSHOP', dt, filename), wayback=False)

    for csv_href in xpath(index_url, '//a[contains(@href, ".csv")]/@href'):
        filename = csv_href.rsplit('/', 1)[-1]
        dt = get_dt_format(filename, '.csv')
        if dt is not None:
            coll.append(PriceList(csv_href, '(internet trgovina)', '', tobylex.id, 'WEBSHOP', dt, filename))

    actual = extract_offers_since(tobylex, coll, min_date, wayback=False)

    prod = []
    for p in actual:
        rows = get_csv_rows(ensure_archived(p, True, wayback=False))
        header = ';'.join(rows[0]).strip('﻿')  # zero-width non-breaking space
        # logger.debug(f'header: {header}')
        for k in rows[1:]:
            if header == '"Naziv firme";Prodajno mjesto;Oblik objekta;Adresa objekta;Oznaka objekta;Broj pohrane;Datum i vrijeme generiranja;Naziv;Šifra;Marka;Barkod (EAN/GTIN);Jedinica mjere;Cijena za jedinicu mjere;Maloprodajna cijena s PDV-om;Valuta;Poseban oblik prodaje;Naziv posebnog oblika prodaje;Sidrena cijena;Datum sidrene cijene;Dostupnost':
                brand, _, _, _, _, _, _, name, _id, brand, barcode, units, ppu, mpc, currency, is_discount, discount_name, anchor_price, anchor_price_date, availability = k
            else:
                val1, val2, name, mpc = k
                barcode = val1 or val2

            if barcode:
                resolve_product(prod, barcode, tobylex, 'WEBSHOP', name, None, mpc, None, None, p.date)

    return prod