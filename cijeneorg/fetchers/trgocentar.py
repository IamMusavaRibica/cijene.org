import io
import zipfile
from datetime import datetime, date

from lxml.etree import XML, XMLParser

from cijeneorg.fetchers.archiver import WaybackArchiver, PriceList
from cijeneorg.fetchers.common import xpath, ensure_archived, resolve_product, extract_offers_since
from cijeneorg.models import Store
from cijeneorg.utils import fix_address, fix_city


def fetch_trgocentar_prices(trgocentar: Store, min_date: date):
    WaybackArchiver.archive(index_url := 'https://trgocentar.com/Trgovine-cjenik/')
    coll = []
    for filename in xpath(index_url, '//a[contains(@href, ".xml") or contains(@href, "_roba_")]/@href'):
        full_url = index_url + filename
        if filename.endswith('.zip'):  # since 17.11.2026. e.g. 84210581427_cjenici_trgovine_roba_20261121_1032.zip
            dt = datetime.strptime(filename[-17:], '%Y%m%d_%H%M.zip')
            coll.append(PriceList(full_url, None, None, trgocentar.id, None, dt, filename))
            continue
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
        data = ensure_archived(p, True, wayback=False)
        if p.filename.endswith('.zip'):  # since 17.11.2026. e.g. 84210581427_PRODAVAONA_Varaždinska_2A_Zlatar_P195_roba_2026004_20261121_0935.xml
            zf = zipfile.ZipFile(io.BytesIO(data))
            xmls = ((n.split('_')[-5], zf.read(n)) for n in zf.namelist() if n.endswith('.xml'))
        else:
            xmls = [(p.location_id, data)]
        for location_id, xml_data in xmls:
            for item in XML(xml_data, XMLParser(recover=True)).findall('cjenik'):  # since 17.11.2026. some have '&#2;'
                name = item.findtext('naziv_art')
                _id = item.findtext('sif_art')
                brand = item.findtext('marka')
                _qty = item.findtext('net_kol') or item.findtext('neto_kolicina')  # since 17.11.2026. neto_kolicina
                unit = item.findtext('jmj')
                mpc = item.findtext('mpc')
                ppu = item.findtext('c_jmj')
                discount_mpc = item.findtext('mpc_pop')  # since 17.11.2026. not given, mpc is the current price
                last_30d_mpc = item.findtext('c_najniza_30')
                may2_price = item.findtext('c_020525')  # since 17.11.2026. not given, only 'bazna_cijena' (without date)
                barcode = item.findtext('ean_kod')
                category = item.findtext('naz_kat')
                resolve_product(prod, barcode, trgocentar, location_id, name, brand, discount_mpc or mpc, _qty, may2_price,
                                p.date)

    return prod
