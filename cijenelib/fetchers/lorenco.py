from datetime import datetime

from loguru import logger

from cijenelib.fetchers._archiver import WaybackArchiver, Pricelist
from cijenelib.fetchers._common import xpath, ensure_archived, resolve_product, get_csv_rows
from cijenelib.models import Store


def fetch_lorenco_prices(lorenco: Store):
    WaybackArchiver.archive(index_url := 'https://lorenco.hr/dnevne-cijene/')
    coll = []
    for a in xpath(index_url, '//a[contains(@href, ".csv")]'):
        href = a.get('href')
        filename = href.split('/')[-1]
        dt_str = a.text.removeprefix('Cijenik ').removeprefix('Cjenik ')  # in case they become literate
        dt = datetime.strptime(dt_str.rstrip('.'), '%d.%m.%Y')
        coll.append(Pricelist(href, None, None, lorenco.id, 'X', dt, filename))

    if not coll:
        logger.warning('no lorenco pricelists found')
        return []

    logger.info(f'found {len(coll)} lorenco pricelists')
    coll.sort(key=lambda x: x.dt, reverse=True)
    today = coll[0].dt.date()
    today_coll = []
    for p in coll:
        if p.dt.date() == today:
            today_coll.append(p)
        else:
            ensure_archived(p, wayback=False)

    prod = []
    for p in today_coll:
        rows = get_csv_rows(ensure_archived(p, True, wayback=False))
        for k in rows[1:]:
            barcode, name, unit, mpc, _datum, _tekst, ppu, _stajeovo, _valuta, may2_price, *_konst = k
            resolve_product(prod, barcode, lorenco, p.location_id, name, mpc, None, may2_price)
    return prod