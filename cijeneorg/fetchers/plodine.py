import io
import re
import zipfile
from datetime import datetime, date

from loguru import logger

from cijeneorg.fetchers.archiver import WaybackArchiver, PriceList
from cijeneorg.fetchers.common import get_csv_rows, resolve_product, xpath, ensure_archived, extract_offers_since
from cijeneorg.models import Store
from cijeneorg.utils import fix_address, fix_city



BLACKLIST = (
    '3856018206685', '4003368140827', '3856012851973', 'KOMPLET X-PLORER PR. SVIJETLO,', '3856012868773',
    '3856018212266', '3800024028045', '3859888679573', '4013265001039', '4013265001114',
)

def fetch_plodine_prices(plodine: Store, min_date: date):
    WaybackArchiver.archive(index_url := 'https://www.plodine.hr/info-o-cijenama')
    coll = []
    for href in xpath(index_url, '//a[contains(@href, "plodine.hr/cjenici/")]/@href'):
        filename = href.rsplit('/', 1)[-1]
        if not filename.endswith('.zip'):
            logger.warning(f'unexpected file href in Plodine prices page: {href}')
            continue
        dt = datetime.strptime(filename, 'cjenici_%d_%m_%Y_%H_%M_%S.zip')
        coll.append(PriceList(href, None, None, plodine.id, None, dt, filename))

    actual = extract_offers_since(plodine, coll, min_date)

    prod = []
    for p in actual:
        zip_data = ensure_archived(p, True, wayback=False)
        try:
            with zipfile.ZipFile(io.BytesIO(zip_data)) as zf:
                for filename in zf.namelist():
                    if not filename.endswith('.csv'):
                        logger.warning(f'unexpected file in Plodine zip: {filename}')
                        continue

                    market_type, *full_addr, location_id, _id, _ = filename.split('_')
                    full_addr = ' '.join(full_addr)
                    five_digit_nums = list(re.finditer(r'\b\d{5}\b', full_addr))
                    if not five_digit_nums:
                        logger.warning(f'failed to parse filename {filename}')
                        continue

                    postal_match = five_digit_nums[-1]
                    address = full_addr[:postal_match.start()].strip()
                    postal_code = postal_match.group(0)
                    city = full_addr[postal_match.end():].strip().title()
                    city = fix_city(city)
                    address = fix_address(address)

                    num_warns = 0
                    with zf.open(filename) as f:
                        rows = get_csv_rows(f.read())
                        header = ';'.join(rows[0])
                        for k in rows[1:]:
                            try:
                                if header == 'Naziv proizvoda;Sifra proizvoda;Marka proizvoda;Jedinica mjere;Cijena po JM;MPC;Poseban oblik prodaje;Naziv posebnog oblika prodaje;Sidrena cijena;Barkod;Dostupno nedostupno;':
                                    name, _id, brand, units, ppu, mpc, is_discount, discount_name, anchor_price, barcode, availability, _ = k
                                    discount_mpc = None
                                    _qty = None
                                else:
                                    name, _id, brand, _qty, units, mpc, ppu, discount_mpc, last_30d_mpc, may2_price, barcode, category, _ = k
                            except:
                                # examples:
                                # ['MJERNE ZLICICE 6/1  817YA  1', '5', '15', '50', '100', '125 ML', '765805', 'KINA - UVOZ', 'KOM', '0,11', ',66', 'NE', '', ',66', '3856018206685', 'NEDOSTUPNO', '']
                                # ['POPLUN 140X200CM', ' 300GR-6 0902G21', '712729', 'KINA - UVOZ', 'KOM', '', '6,63', 'NE', '', '6,63', '3856012851973', 'NEDOSTUPNO', '']
                                # ['KOSARE UKRASNE 3/1 36*25*20', ' 29*21*16', ' 25*16*12 CMSIVE 14082', '783600', 'NJEMACKA - UNOS', 'KOM', '11,94', '11,94', 'NE', '', '11,94', '4003368140827', 'NEDOSTUPNO', '']
                                if any(b in k for b in BLACKLIST):
                                    continue
                                num_warns += 1
                                if num_warns <= 3:
                                    logger.warning('invalid row {}', k)
                                continue
                            resolve_product(prod, barcode, plodine, location_id, name, brand, discount_mpc or mpc, _qty, None, p.date)

        except Exception as e:
            logger.error(f'failed to process Plodine zip {p.filename}: {e}')
            continue
    return prod
