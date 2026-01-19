from datetime import datetime, date

from cijeneorg.fetchers.archiver import WaybackArchiver, PriceList
from cijeneorg.fetchers.common import xpath, ensure_archived, resolve_product, get_csv_rows, extract_offers_since
from cijeneorg.models import Store


def fetch_lorenco_prices(lorenco: Store, min_date: date):
    WaybackArchiver.archive(index_url := 'https://lorenco.hr/dnevne-cijene/')
    coll = []
    for a in xpath(index_url, '//a[contains(@href, ".csv")]'):
        href = a.get('href')
        filename = href.split('/')[-1]
        dt_str = (a.text.removeprefix('_')
                  .removeprefix('Cijenik')
                  .removeprefix('Cjenik')
                  .removeprefix('Cijene')
                  .removesuffix('2024.')
                  .lstrip())

        __replacements = {
            '08.01.2025.': '08.01.2026.',  # bruh.
            '10.07.': '10.07.2025.',
            '30.09': '30.09.2025.',
        }
        dt_str = __replacements.get(dt_str, dt_str)

        if dt_str == '.2025.':
            continue
        elif dt_str.endswith('2025') or dt_str.endswith('2026'):
            dt_str += '.'

        dt = datetime.strptime(dt_str.removesuffix('.'), '%d.%m.%Y')
        if dt.year == 2025 and dt.month < 5:
            dt = dt.replace(year=2026)
        coll.append(PriceList(href, None, None, lorenco.id, 'X', dt, filename))

    actual = extract_offers_since(lorenco, coll, min_date)

    prod = []
    for p in actual:
        rows = get_csv_rows(ensure_archived(p, True, wayback=False))
        for k in rows[1:]:
            barcode, name, unit, mpc, _datum, _tekst, ppu, _stajeovo, _valuta, may2_price, *_konst = k
            resolve_product(prod, barcode, lorenco, p.location_id, name, None, mpc, None, may2_price, p.date)
    return prod
