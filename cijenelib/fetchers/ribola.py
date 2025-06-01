import concurrent.futures

import requests
from loguru import logger
from lxml.etree import HTML, XML, tostring

from cijenelib.fetchers.common import cached_fetch, resolve_product
from cijenelib.models import Store
from cijenelib.products import AllProducts

BASE_URL = 'https://ribola.hr/ribola-cjenici/'
def fetch_ribola_prices(ribola: Store):
    today_url = BASE_URL + HTML(requests.get(BASE_URL).content) \
                            .xpath('//tr[2]/td/a/@href')[0]

    # scrape the webpage to find download links
    root0 = HTML(requests.get(today_url).content)
    hrefs = []
    for tr in root0.xpath('//tr'):
        if tr.find('th') is not None:  # skip header rows
            continue
        if anchor := tr.xpath('.//a[@download]'):
            hrefs.append(anchor[0].get('href'))
        else:
            logger.warning(f'No download link found in row: {tostring(tr, pretty_print=True)}')

    # one file = one request so we can use concurrency
    all_products = []
    # with concurrent.futures.ThreadPoolExecutor(max_workers=min(25, len(hrefs)), thread_name_prefix='Ribola') as executor:
    #     futures = [executor.submit(process_single, BASE_URL + h, ribola) for h in hrefs]
    #     for fut in concurrent.futures.as_completed(futures):
    #         try:
    #             if result := fut.result():
    #                 all_products.extend(result)
    #         except Exception as e:
    #             logger.error(f'Error processing ribola href: {e!r}')
    for h in hrefs:
        try:
            all_products.extend(process_single(BASE_URL + h, ribola))
        except Exception as e:
            logger.error(f'error processing ribola href {h}: {e!r}')
    return all_products


def process_single(full_url: str, ribola: Store):
    root = XML(cached_fetch(full_url)
               .replace(b'MaloprmdajnaCijenaAkcija', b'MaloprodajnaCijenaAkcija'))
    coll = []
    for prodajni_objekt in root.findall('ProdajniObjekt'):
        location_id = prodajni_objekt.findtext('Oznaka')
        logger.debug(f'processing store {location_id} from {full_url}')
        for k in prodajni_objekt.find('Proizvodi').findall('Proizvod'):
            name: str = k.findtext('NazivProizvoda')
            _id = k.findtext('SifraProizvoda')
            brand = k.findtext('MarkaProizvoda')
            total_qty = k.findtext('NetoKolicina')
            unit = k.findtext('JedinicaMjere')
            mpc = k.findtext('MaloprodajnaCijena')
            ppu = k.findtext('CijenaZaJedinicuMjere')
            discount_mpc = k.findtext('MaloprodajnaCijenaAkcija')
            last_30d_mpc = k.findtext('NajnizaCijena')
            may2_price = k.findtext('SidrenaCijena')
            barcode = k.findtext('Barkod')
            category = k.findtext('KategorijeProizvoda')

            if not barcode:
                continue

            while '  ' in name:
                name = name.replace('  ', ' ')

            name = name.strip().replace('GA ZIRANI', 'GAZIRANI') \
                .replace('G AZIRANI', 'GAZIRANI') \
                .replace(' P ET', ' PET') \
                .replace(' PE T', ' PET') \
                .replace('lE T GAZIRANI SOK', 'l PET GAZIRANI SOK') \
                .replace('lE T', 'l PET') \
                .replace('0, 5', '0,5') \

            if name.endswith('l P'):
                name = name[:-3] + 'l PET'

            fixed_name = name.replace(' PET GAZIRANI SOK', '') \
                .replace(' PET GAZIRANI S', '') \
                .replace(' l PET', ' l') \
                .replace(' l P', ' l') \
                .replace(' 5+1 GRATIS LIM.', '') \
                .replace(' GAZIRANI SOK', '') \

            try:
                *_, total_qty, unit = fixed_name.rsplit(maxsplit=2)
                quantity = float(total_qty.replace(',', '.'))
            except ValueError:  # can be thrown when unpacking or converting to float fails
                if barcode in AllProducts:
                    logger.warning(f'didnt parse product {barcode} `{name}` = `{fixed_name}` {total_qty =}')
                continue

            price = mpc or discount_mpc
            if not price:
                logger.warning(f'product {name}, barcode {barcode} has no current price')
                continue
            price = float(price)
            may2_price = float(may2_price) if may2_price else None

            resolve_product(coll, barcode, ribola, location_id, name, price, quantity, may2_price)
    return coll