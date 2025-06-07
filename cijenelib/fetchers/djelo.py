from datetime import datetime
from urllib.parse import unquote

from loguru import logger

from cijenelib.fetchers._archiver import Pricelist, WaybackArchiver
from cijenelib.fetchers._common import xpath, ensure_archived
from cijenelib.models import Store
from cijenelib.utils import fix_address, fix_city


def fetch_djelo_prices(djelo: Store):
    WaybackArchiver.archive(index_url := 'https://cjenik.djelo.hr/')
    coll = []
    for url in xpath(index_url, '//a[contains(@href, ".xlsx")]/@href'):
        full_url = index_url + url
        try:
            filename = (unquote(url).replace('JELA?I?A', 'JELAČIĆA')
                        .replace('?IBENIK', 'ŠIBENIK')
                        .replace('RA?INE', 'RAŽINE'))
            market_type, address, city, location_id, file_id, dtstr = filename.split('#')
            dt = datetime.strptime(dtstr, '%Y-%m-%dT%H%M%S.xlsx')
            coll.append(Pricelist(full_url, fix_address(address), fix_city(city), djelo.id, location_id, dt, filename))
        except Exception as e:
            logger.warning(f'error {e!r} while parsing metadata for djelo vodice pricelist {url}')
            logger.exception(e)
            continue

    if not coll:
        logger.warning('no djelo vodice pricelists found')
        return []

    coll.sort(key=lambda x: x.dt, reverse=True)
    today = coll[0].dt.date()
    today_coll = []
    for p in coll:
        if p.dt.date() == today:
            today_coll.append(p)
        else:
            ensure_archived(p, wayback=False)

    prod = []
    for t in today_coll:
        raw_xlsx = ensure_archived(t, True, wayback=False)
        # TODO: implement parsing xlsx files!

    return prod