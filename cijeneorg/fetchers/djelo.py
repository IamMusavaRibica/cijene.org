from datetime import datetime
from urllib.parse import unquote

from loguru import logger

from cijeneorg.fetchers.archiver import Pricelist, WaybackArchiver
from cijeneorg.fetchers.common import xpath, ensure_archived, extract_offers_from_today
from cijeneorg.models import Store
from cijeneorg.utils import fix_address, fix_city


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

    today_coll = extract_offers_from_today(djelo, coll)

    prod = []
    for t in today_coll:
        raw_xlsx = ensure_archived(t, True, wayback=False)
        # TODO: implement parsing xlsx files!

    return prod