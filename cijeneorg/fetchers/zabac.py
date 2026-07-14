import base64
import re
from collections import defaultdict
from datetime import datetime, date

from loguru import logger
from lxml.etree import tostring

from cijeneorg.fetchers.archiver import WaybackArchiver, PriceList
from cijeneorg.fetchers.common import xpath, ensure_archived, get_csv_rows, resolve_product
from cijeneorg.models import Store

# date_pattern = re.compile(r'Cjenik-(\d{1,2}\.?\d{1,2}\.?\d{4})')
# date_pattern2 = re.compile(r'(?:10000|10410)-(\d{1,2}\.?\d{1,2}\.?\d{4})')
date_pattern3 = re.compile(r'(\d{2}\.\d{2}\.\d{4}),\s*(\d{1,2}\.\d{2})h')

def fetch_zabac_prices(zabac: Store, min_date: date):
    coll = []
    urls = []

    pages = [
        'https://zabacfoodoutlet.hr/cjenik?store=Dubec%2C%20Dubrava',
        'https://zabacfoodoutlet.hr/cjenik?store=Velika%20Gorica'
    ]
    pricelist_row_xpath = "//article[contains(concat(' ', normalize-space(@class), ' '), ' idk_pricelist_row ')]"
    for page in pages:
        WaybackArchiver.archive(page)
        rows, root = xpath(page, pricelist_row_xpath, return_root=True)
        # today date price list is in a separate element

        try:
            today = root.xpath('//div[@class="idk_pricelist_featured"]')[0]
            store0 = today.xpath('.//h3/text()')[0]
            download0 = today.xpath('.//a[@class="idk_pricelist_download_btn"]/@href')[0]
            urls.append((store0, download0))
        except Exception as e:
            logger.exception('failed to parse today\'s zabac pricelist')
        for row in rows:
            h3_text = row.xpath(".//h3/text()")
            csv_url = row.xpath(".//a[contains(@class, 'idk_pricelist_row_download')]/@href")

            h3_text = h3_text[0].strip() if h3_text else None
            csv_url = csv_url[0].strip() if csv_url else None

            key = (h3_text, csv_url)
            if None in key:
                logger.warning(f'skipping zabac pricelist row with missing h3 text or csv url: {tostring(row)}')

            urls.append(key)

    for storeinfo, url in urls:
        try:
            filename = url.rsplit('/', 1)[-1]
            m = date_pattern3.search(storeinfo)
            if not m:
                logger.warning(f'failed to parse zabac pricelist date from filename: {filename}')
                continue
            datestr = m.group(1)
            timestr = m.group(2)
            dt = datetime.strptime(f'{datestr} {timestr}', '%d.%m.%Y %H.%M')

            address, city, location_id = '???', '???', 'PJ-?'
            fl = filename.lower()
            if 'dubrava' in fl and '256l' in fl:
                address = 'Avenija Dubrava 256L'
                city = 'Zagreb'
                location_id = 'PJ-?'
            elif '10410' in fl and 'velika' in fl and 'gorica' in fl:
                address = 'Trg grada Vukovara 8'
                city = 'Velika Gorica'
                location_id = 'PJ-9'

            # if datestr.count('.') == 2:
            #     dt = datetime.strptime(datestr, '%d.%m.%Y')
            # else:
            #     dt = datetime.strptime(datestr, '%d%m%Y')
            coll.append(PriceList(url, address, city, zabac.id, location_id, dt, filename))
        except Exception as e:
            logger.warning(f'failed to parse zabac pricelists: {url}')
            logger.exception(e)
            continue

    if not coll:
        logger.warning('no zabac pricelists found!')
        return []

    logger.info(f'found {len(coll)} zabac pricelists')

    prod = []
    warned = defaultdict(bool)
    for t in coll:
        rows = get_csv_rows(ensure_archived(t, True, wayback=False))
        header = ';'.join(rows[0]).strip().strip('\ufeff')
        for k in rows[1:]:
            qty = None
            may2_price = None
            brand = None
            HEADER_TYPE_1 = {'Artikl Šifra;Barcode;Pdv %;Naziv artikla / usluge;MPC'}
            HEADER_TYPE_2 = {'Artikl;Pdv %;Naziv grupe artikla;Barcode;Naziv artikla / usluge;Mpc'}
            HEADER_TYPE_3 = {
                'Artikl;Naziv grupe artikla;Pdv %;Barcode;Naziv artikla / usluge;Mpc;Marka;Gramaža;Najniža cijena u posljednjih 30 dana;Sidrena cijena na 2.5.2025',
                'Artikl;Naziv grupe artikla;Pdv %;Barcode;Naziv artikla;MPC;Marka;Gramaža;Najniža cijena u posljednjih 30 dana;Sidrena cijena na 2.5.2025',
                'Artikl;Naziv grupe artikala;Pdv %;Barcode;Naziv artikla;MPC;Marka;Gramaža;Najniža cijena u posljednjih 30 dana;Sidrena cijena na 2.5.2025',
                'Šifra artikla;Naziv grupe artikala;PDV;Barcode;Naziv artikla;MPC;Marka;Gramaža;Najniža cijena u posljednjih 30 dana;Sidrena cijena na 2.5.2025',
                'Šifra;Naziv grupe artikala;PDV;Barcode;Naziv artikla;MPC;Marka;Gramaža;Najniža cijena u posljednjih 30 dana;Sidrena cijena na 2.5.2025',
                'ŠIFRA ARTIKLA,NAZIV GRUPE ARTIKALA,PDV,BARCODE,NAZIV ARTIKLA,MPC,Marka,Gramaža,Najniža cijena u posljednjih 30 dana,Sidrena cijena na 2.5.2025',
                'ŠIFRA ARTIKLA;NAZIV GRUPE ARTIKALA;PDV;BARCODE;NAZIV ARTIKLA;MPC;Marka;Gramaža;Najniža cijena u posljednjih 30 dana;Sidrena cijena na 2.5.2025',
            }
            if header in HEADER_TYPE_1:
                _id, barcode, vat, name, mpc = k
            elif header in HEADER_TYPE_2:
                _id, vat, category, barcode, name, mpc = k
            elif header in HEADER_TYPE_3:
                if len(k) == 10:
                    _id, category, vat, barcode, name, mpc, brand, qty, last_30d_mpc, may2_price = k
                # elif k[:1] == k[-1:] == '"':
                    # see https://zabacfoodoutlet.hr/wp-content/uploads/2026/02/SupermarketDubrava-256L-Zagreb-10000-4.2.2026-7.00h-C180-1.csv
                    # import ast
                    # k2 = ast.literal_eval(f'[{k[1:-1]}]')
                    # _id, category, vat, barcode, name, mpc, brand, qty, last_30d_mpc, may2_price = k2
                else:
                    logger.warning(f'unexpected row format in zabac pricelist {t.filename}: {k}')
                    continue
            else:
                if not warned[header]:
                    logger.warning('\nZABAC UNKNOWN HEADER: {}', header)
                    logger.debug(base64.b64encode(header.encode()).decode())
                    warned[header] = True
                continue
            if '+' in barcode:  # scientific notation for barcode, really ?
                continue
            resolve_product(prod, barcode, zabac, t.location_id, name, brand, mpc, qty, may2_price, t.date)

    return prod
