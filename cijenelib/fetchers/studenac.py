import io
import re
import zipfile
from datetime import date

import requests
from loguru import logger
from lxml.etree import XML, HTML, tostring

from cijenelib.models import Store
from .common import cached_fetch, resolve_product
from ..products import AllProducts

pattern = re.compile(r"PROIZVODI-(\d{4})-(\d{2})-(\d{2})\.zip")
def fetch_studenac_prices(studenac: Store):
    prefix = 'https://www.studenac.hr/cjenici/'
    base_url = 'https://www.studenac.hr/popis-maloprodajnih-cijena'
    tree = HTML(requests.get(base_url).content)

    target_url = (date.fromordinal(1), '')
    for a in tree.xpath(f'//a[starts-with(@href, "{prefix}")]'):
        href = a.get('href')
        if m := pattern.match(href.removeprefix(prefix)):
            year, month, day = map(int, m.groups())
            dd = date(year, month, day)
            if dd > target_url[0]:
                target_url = (dd, a.get('href'))
        else:
            logger.warning(f'unexpected anchor: {tostring(a)}')

    raw = cached_fetch(target_url[1])

    # monkey-patch the zipfile.ZipFile.open method to avoid comparing header and actual file names
    # which would raise a BadZipFile exception if they mismatch
    orig_code, new_code = monkeypatch_zipfile_open()

    prod = []
    with zipfile.ZipFile(io.BytesIO(raw)) as zf:
        for filename in zf.namelist():
            with zf.open(filename) as file:
                xml_data = file.read()
                root = XML(xml_data)
                for prodajni_objekt in root.findall('ProdajniObjekt'):
                    location_id = prodajni_objekt.findtext('Oznaka')
                    if location_id not in studenac.locations:
                        logger.warning(f'studenac {location_id} unknown store!')

                    logger.debug(f'processing store {location_id} from file {filename}')
                    for k in prodajni_objekt.find('Proizvodi').findall('Proizvod'):
                        # findtext returns '' if it does not exist
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
                        fixed_name = name.replace(' 6*0,15 l', ' 0,9 l') \
                                         .replace(' 0,15l x12 LIM NO SUGAR', ' 1,8 l') \
                                         .replace(' 2*2L', ' 4 l') \
                                         .replace(' 150 ML 12/1', ' 1,8 l')

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

                        resolve_product(prod, barcode, studenac, location_id, name, price, quantity, may2_price)

    # restore the original method, just in case
    zipfile.ZipFile.open.__code__ = orig_code
    return prod

def monkeypatch_zipfile_open():
    orig = zipfile.ZipFile.open
    orig_code = zipfile.ZipFile.open.__code__
    import dis, sys
    if sys.version_info.minor not in {12}:
        logger.warning(f'attempting to monkey-patch on Python 3.{sys.version_info.minor}, this may not work')
    instrs = list(dis.get_instructions(orig))
    for idx, ins in enumerate(instrs[1:], start=1):
        if ins.opname == 'LOAD_CONST' and ins.argval == 'File name in directory ':
            wanted = instrs[idx-1]
            cond_jump = instrs[idx-2]
            # print(f'Found {wanted = }')
            # print(f'Found {cond_jump = }')
            # put a JUMP_FORWARD after POP_JUMP_IF_FALSE so it always jumps, never reaches the exception code
            raw_bytecode = list(orig_code.co_code)
            raw_bytecode[wanted.offset] = dis.opmap['JUMP_FORWARD']
            raw_bytecode[wanted.offset + 1] = cond_jump.arg - 1
            new_code = zipfile.ZipFile.open.__code__ = orig.__code__.replace(co_code=bytes(raw_bytecode))
            break
    else:
        raise RuntimeError('monkey-patch failed')

    return orig_code, new_code
