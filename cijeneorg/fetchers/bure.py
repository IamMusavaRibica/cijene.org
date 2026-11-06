import io
import zipfile
from datetime import datetime, date
from urllib.parse import unquote

from loguru import logger
from lxml.etree import XML

from cijeneorg.fetchers.archiver import WaybackArchiver, PriceList
from cijeneorg.fetchers.common import xpath, ensure_archived, resolve_product, extract_offers_since
from cijeneorg.models import Store
from cijeneorg.utils import fix_address, fix_city, UA_HEADER


def fetch_bure_prices(bure: Store, min_date: date):
    # what's the difference between this and https://www.bure.hr/index.php/cjenici-arhiva ?
    # TODO: bure has pages now: ?page=2
    WaybackArchiver.archive(index_url := 'https://www.bure.hr/cjenici-arhiva')
    coll = []
    hrefs = []
    roots = []
    for page in (1, 2):
        href_list, root = xpath(f'{index_url}?page={page}', '//a[contains(@href, ".xml")]/@href', extra_headers=UA_HEADER, return_root=True)
        logger.debug(f'extending with {len(href_list)} hrefs on page {page}')
        hrefs.extend(href_list)
        roots.append(root)
    logger.debug(f'{len(hrefs)},\n{"\n".join(hrefs)}')
    for href in hrefs:
        filename = unquote(href.rsplit('/', 1)[-1])
        market_type, address, location_id, file_id, rest = filename.split('-', 4)
        i = 3 if address.endswith('BIOGRAD_NA_MORU') else 1
        address, *city = address.rsplit('_', i)
        address = fix_address(address.replace('_', ' '))
        city = fix_city(' '.join(city))
        dt = datetime.strptime(rest.replace('-', '')[:14], '%Y%m%d%H%M%S')
        p = PriceList(href, address, city, bure.id, location_id, dt, filename)
        p.request_kwargs = {'headers': UA_HEADER}
        ensure_archived(p, wayback=False)
        # coll.append(p)
    # just archive the xmls  ^^
    # but fetch the zip because sometimes xml is 404 because of weird filename
    for root in roots:
        for tr in root.xpath('//tr[@class="pricelist-row"]'):
            zip_href = tr.xpath('.//a[contains(@href, "preuzmi-zip")]/@href')[0]
            dt = datetime.strptime(tr.get('data-date'), '%d.%m.%Y')
            filename = f'bure_price_file_{dt:%Y-%m-%d}.zip'
            p = PriceList(zip_href, None, None, bure.id, '???', dt, filename)
            p.request_kwargs = {'headers': UA_HEADER}
            coll.append(p)

    logger.debug(f'coll len: {len(coll)}')
    actual = extract_offers_since(bure, coll, min_date)

    prod = []
    for p in actual:
        zip_data = ensure_archived(p, True)
        with zipfile.ZipFile(io.BytesIO(zip_data)) as zf:
            for filename in zf.namelist():
                if not filename.endswith('.xml'):
                    logger.warning(f'unexpected file in bure zip: {filename}')
                    continue

                with zf.open(filename) as f:
                    root = XML(f.read())
                    for prodajni_objekt in root.findall('ProdajniObjekt'):
                        for k in prodajni_objekt.find('Proizvodi').findall('Proizvod'):
                            name: str = k.findtext('NazivProizvoda')
                            _id = k.findtext('SifraProizvoda')
                            brand = k.findtext('MarkaProizvoda')
                            _qty = k.findtext('NetoKolicina')
                            unit = k.findtext('JedinicaMjere')
                            mpc = k.findtext('MaloprodajnaCijena')
                            ppu = k.findtext('CijenaZaJedinicuMjere')
                            discount_mpc = k.findtext('MaloprodajnaCijenaAkcija')
                            last_30d_mpc = k.findtext('NajnizaCijena')
                            may2_price = k.findtext('SidrenaCijena')
                            barcode = k.findtext('Barkod')
                            category = k.findtext('KategorijeProizvoda')
                            resolve_product(prod, barcode, bure, p.location_id, name, brand, discount_mpc or mpc, _qty,
                                            may2_price, p.date)

    return prod
