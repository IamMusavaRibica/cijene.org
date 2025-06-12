import io
import re
import zipfile
from datetime import datetime

from loguru import logger
from lxml.etree import XML

from cijeneorg.models import Store
from .archiver import WaybackArchiver, Pricelist
from .common import resolve_product, xpath, ensure_archived
from ..utils import remove_extra_spaces

pattern = re.compile(r"PROIZVODI-(\d{4})-(\d{2})-(\d{2})\.zip")
PREFIX = 'https://www.studenac.hr/cjenici/'
BASE_URL = 'https://www.studenac.hr/popis-maloprodajnih-cijena'
def fetch_studenac_prices(studenac: Store):
    WaybackArchiver.archive(BASE_URL)
    coll = []
    for href in xpath(BASE_URL, f'//a[starts-with(@href, "{PREFIX}")]/@href'):
        filename = href.removeprefix(PREFIX)
        dt = datetime.strptime(filename, 'PROIZVODI-%Y-%m-%d.zip')
        coll.append(Pricelist(href, None, None, studenac.id, None, dt, filename))

    if not coll:
        logger.warning('no studenac pricelists found')
        return []

    logger.info(f'found {len(coll)} studenac pricelists')
    coll.sort(key=lambda x: x.dt, reverse=True)
    today = coll[0].dt.date()
    today_coll = []
    for p in coll:
        if p.dt.date() == today:
            today_coll.append(p)
        else:
            ensure_archived(p)

    # monkey-patch the zipfile.ZipFile.open method to avoid comparing header and actual file names
    # which would raise a BadZipFile exception if they mismatch
    orig_code, new_code = monkeypatch_zipfile_open()

    prod = []
    for p in today_coll:
        zip_data = ensure_archived(p, True)
        with zipfile.ZipFile(io.BytesIO(zip_data)) as zf:
            for filename in zf.namelist():
                if not filename.endswith('.xml'):
                    logger.warning(f'unexpected file in studenac zip: {filename}')
                    continue

                with zf.open(filename) as f:
                    root = XML(f.read())
                    for prodajni_objekt in root.findall('ProdajniObjekt'):
                        location_id = prodajni_objekt.findtext('Oznaka')
                        if location_id not in studenac.locations:
                            logger.warning(f'studenac {location_id} unknown store!')
                        for k in prodajni_objekt.find('Proizvodi').findall('Proizvod'):
                            # findtext returns '' if it does not exist
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

                            name = (remove_extra_spaces(name)
                                    .replace(' 6*0,15 l', ' 0,9 l')
                                    .replace(' 0,15l x12 LIM NO SUGAR', ' 1,8 l')
                                    .replace(' 2*2L', ' 4 l')
                                    .replace(' 150 ML 12/1', ' 1,8 l'))

                            resolve_product(prod, barcode, studenac, location_id, name, discount_mpc or mpc, _qty, may2_price)

    # restore the original method
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
