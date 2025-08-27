from datetime import datetime, date

from lxml.etree import XML

from cijeneorg.fetchers.archiver import WaybackArchiver, PriceList
from cijeneorg.fetchers.common import xpath, ensure_archived, resolve_product, extract_offers_since
from cijeneorg.models import Store
from cijeneorg.utils import fix_address, fix_city


def fetch_trgocentar_prices(trgocentar: Store, min_date: date):
    WaybackArchiver.archive(index_url := 'https://trgocentar.com/Trgovine-cjenik/')
    coll = []
    for filename in xpath(index_url, '//a[contains(@href, ".xml")]/@href'):
        full_url = index_url + filename
        market_type, *full_addr, location_id, file_id, date_str = filename.split('_')
        i = 1
        for t in {'HUM_NA_SUTLI', 'SV_IVAN_ZELINA', 'SV_KRIZ_ZACRETJE', }:
            if t in filename:
                i += t.count('_')
        address, city = full_addr[:-i], full_addr[-i:]
        address = fix_address(' '.join(address))
        city = fix_city(' '.join(city))
        dt = datetime.strptime(date_str, '%d%m%Y%H%M.xml')
        coll.append(PriceList(full_url, address, city, trgocentar.id, location_id, dt, filename))

    actual = extract_offers_since(trgocentar, coll, min_date)

    prod = []
    for p in actual:
        root = XML(ensure_archived(p, True, wayback=False))
        for item in root.findall('cjenik'):
            name = item.findtext('naziv_art')
            _id = item.findtext('sif_art')
            brand = item.findtext('marka')
            _qty = item.findtext('net_kol')
            unit = item.findtext('jmj')
            mpc = item.findtext('mpc')
            ppu = item.findtext('c_jmj')
            discount_mpc = item.findtext('mpc_pop')
            last_30d_mpc = item.findtext('c_najniza_30')
            may2_price = item.findtext('c_020525')
            barcode = item.findtext('ean_kod')
            category = item.findtext('naz_kat')
            resolve_product(prod, barcode, trgocentar, p.location_id, name, discount_mpc or mpc, _qty, may2_price,
                            p.date)

    return prod
