from datetime import datetime, date

from lxml.etree import XML

from cijeneorg.fetchers.archiver import WaybackArchiver, PriceList
from cijeneorg.fetchers.common import xpath, ensure_archived, resolve_product, extract_offers_since
from cijeneorg.models import Store


def fetch_shome_prices(shome: Store, min_date: date):
    # one price list for all stores, location_id hardcoded as X
    WaybackArchiver.archive(index_url := 'https://www.shome.hr/cjenik-arhiva/')
    coll = []
    for href in xpath(index_url, '//a[contains(@href, ".xml")]/@href'):
        filename = href.rsplit('/', 1)[-1]  # sidrena-cijena_22-11-2026.xml
        dt = datetime.strptime(filename, 'sidrena-cijena_%d-%m-%Y.xml')
        coll.append(PriceList(index_url + filename, None, None, shome.id, 'X', dt, filename))

    actual = extract_offers_since(shome, coll, min_date)

    prod = []
    for p in actual:
        root = XML(ensure_archived(p, True, wayback=False))
        for item in root.findall('proizvod'):
            name = item.findtext('naziv')
            mpc = item.findtext('maloprodajna_cijena')  # already includes the discount (poseban_oblik_prodaje)
            may2_price = item.findtext('sidrena_cijena')
            if not item.findtext('sidreni_datum', '').startswith('02.05.2025'):  # usually 10.09.2026.
                may2_price = None
            barcode = item.findtext('barkod')
            resolve_product(prod, barcode, shome, p.location_id, name, None, mpc, None, may2_price, p.date)

    return prod
