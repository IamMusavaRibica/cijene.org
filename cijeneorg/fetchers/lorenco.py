from datetime import datetime

from loguru import logger

from cijeneorg.fetchers.archiver import WaybackArchiver, PriceList
from cijeneorg.fetchers.common import xpath, ensure_archived, resolve_product, get_csv_rows, extract_offers_from_today
from cijeneorg.models import Store


def fetch_lorenco_prices(lorenco: Store):
    WaybackArchiver.archive(index_url := 'https://lorenco.hr/dnevne-cijene/')
    coll = []
    for a in xpath(index_url, '//a[contains(@href, ".csv")]'):
        href = a.get('href')
        filename = href.split('/')[-1]
        dt_str = (a.text.removeprefix('Cijenik ')
                  .removeprefix('Cjenik ')  # in case they become literate
                  .removeprefix('Cijene '))
        dt = datetime.strptime(dt_str.rstrip('.'), '%d.%m.%Y')
        coll.append(PriceList(href, None, None, lorenco.id, 'X', dt, filename))

    today_coll = extract_offers_from_today(lorenco, coll)

    prod = []
    for p in today_coll:
        rows = get_csv_rows(ensure_archived(p, True, wayback=False))
        for k in rows[1:]:
            barcode, name, unit, mpc, _datum, _tekst, ppu, _stajeovo, _valuta, may2_price, *_konst = k
            resolve_product(prod, barcode, lorenco, p.location_id, name, mpc, None, may2_price)
    return prod