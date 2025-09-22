from cijeneorg.fetchers import (
    fetch_bakmaz_prices,
    fetch_boso_prices,
    fetch_brodokomerc_prices,
    fetch_bure_prices,
    fetch_croma_prices,
    fetch_djelo_prices,
    fetch_djelo_vodice_prices,
    fetch_dm_prices,
    fetch_eurospin_prices,
    fetch_jadranka_prices,
    fetch_jedinstvo_labin_prices,
    fetch_kaufland_prices,
    fetch_konzum_prices,
    fetch_ktc_prices,
    fetch_lidl_prices,
    fetch_lorenco_prices,
    fetch_metro_prices,
    fetch_ntl_prices,
    fetch_plodine_prices,
    fetch_radenska_prices,
    fetch_ribola_prices,
    fetch_rotodinamic_prices,
    fetch_spar_prices,
    fetch_stridon_prices,
    fetch_studenac_prices,
    fetch_tobylex_prices,
    fetch_tommy_prices,
    fetch_travelfree_prices,
    fetch_trgocentar_prices,
    fetch_trgovina_krk_prices,
    fetch_vrutak_prices,
    fetch_zabac_prices,
)
from cijeneorg.models import Store
from cijeneorg.store_locations import StoreLocations

Tommy       = Store(name='Tommy',           url='https://www.tommy.hr/',            fetch_prices=fetch_tommy_prices)
Konzum      = Store(name='Konzum',          url='https://www.konzum.hr/',           fetch_prices=fetch_konzum_prices)
Spar        = Store(name='Spar',            url='https://www.spar.hr/',             fetch_prices=fetch_spar_prices)
Studenac    = Store(name='Studenac Market', url='https://www.studenac.hr/',         fetch_prices=fetch_studenac_prices, id='studenac')
Ribola      = Store(name='Ribola',          url='https://ribola.hr/',               fetch_prices=fetch_ribola_prices)
Lidl        = Store(name='Lidl',            url='https://www.lidl.hr/',             fetch_prices=fetch_lidl_prices)
Plodine     = Store(name='Plodine',         url='https://www.plodine.hr/',          fetch_prices=fetch_plodine_prices)
Eurospin    = Store(name='Eurospin',        url='https://www.eurospin.hr/',         fetch_prices=fetch_eurospin_prices)
Kaufland    = Store(name='Kaufland',        url='https://www.kaufland.hr/',         fetch_prices=fetch_kaufland_prices)
Metro       = Store(name='Metro',           url='https://www.metro-cc.hr/',         fetch_prices=fetch_metro_prices)
Boso        = Store(name='Boso',            url='https://www.boso.hr/',             fetch_prices=fetch_boso_prices)
NTL         = Store(name='NTL',             url='https://www.ntl.hr/',              fetch_prices=fetch_ntl_prices)
KTC         = Store(name='KTC',             url='https://www.ktc.hr/',              fetch_prices=fetch_ktc_prices)
TrgovinaKrk = Store(name='Trgovina Krk',    url='https://trgovina-krk.hr/',         fetch_prices=fetch_trgovina_krk_prices)
Bakmaz      = Store(name='Bakmaz',          url='https://www.bakmaz.hr/',           fetch_prices=fetch_bakmaz_prices)
DjeloVodice = Store(name='Djelo Vodice',    url='https://djelo-vodice.hr/',         fetch_prices=fetch_djelo_vodice_prices)
Djelo       = Store(name='Djelo',           url='https://djelo.hr/',                fetch_prices=fetch_djelo_prices)
Zabac       = Store(name='Žabac Food Outlet', url='https://zabacfoodoutlet.hr/',    fetch_prices=fetch_zabac_prices, id='zabac')
Vrutak      = Store(name='Vrutak',          url='https://www.vrutak.hr/',           fetch_prices=fetch_vrutak_prices)
Bure        = Store(name='Bure',            url='https://www.bure.hr/',             fetch_prices=fetch_bure_prices)
Jadranka    = Store(name='Jadranka',        url='https://jadranka-trgovina.com/',   fetch_prices=fetch_jadranka_prices)
Trgocentar  = Store(name='Trgocentar',      url='https://trgocentar.com/',          fetch_prices=fetch_trgocentar_prices)
Lorenco     = Store(name='Lorenco',         url='https://lorenco.hr/',              fetch_prices=fetch_lorenco_prices)
Rotodinamic = Store(name='Roto dinamic',    url='https://www.rotodinamic.hr/',      fetch_prices=fetch_rotodinamic_prices)
Brodokomerc = Store(name='Brodokomerc',     url='http://brodokomerc.hr/',           fetch_prices=fetch_brodokomerc_prices)
Radenska    = Store(name='Radenska',        url='https://www.radenska.hr/',         fetch_prices=fetch_radenska_prices)
JedinstvoLabin = Store(name='Jedinstvo Labin',  url='https://www.jedinstvo-labin.hr/', fetch_prices=fetch_jedinstvo_labin_prices)
Croma       = Store(name='Croma-Varaždin',  url='https://croma.com.hr/',            fetch_prices=fetch_croma_prices, id='croma')
Travelfree  = Store(name='Travel FREE',     url='https://travelfree.hr/',           fetch_prices=fetch_travelfree_prices, id='travelfree')
Tobylex     = Store(name='Tobylex',         url='https://tobylex.net/',             fetch_prices=fetch_tobylex_prices)
DM          = Store(name="DM",              url="https://www.dm.hr/",               fetch_prices=fetch_dm_prices)
Stridon     = Store(name='Stridon',         url='https://www.stridon.hr/',          fetch_prices=fetch_stridon_prices)

ALL_STORES = [Tommy, Konzum, Spar, Studenac, Ribola, Lidl, Plodine, Eurospin, Kaufland, Metro, Boso, NTL, KTC,
              TrgovinaKrk, Bakmaz, DjeloVodice, Djelo, Zabac, Vrutak, Bure, Jadranka, Trgocentar, Lorenco, Rotodinamic,
              Brodokomerc, Radenska, JedinstvoLabin, Croma, Travelfree, Tobylex, DM, Stridon]

ALL_STORES_BY_ID = {s.id: s for s in ALL_STORES}

for store in ALL_STORES:
    for loc_id, loc_data in StoreLocations.get(store.id, {}).items():
        if not loc_data:
            continue
        city = loc_data[0]
        address = loc_data[2]
        lat, lng = map(lambda t: round(t, 6), loc_data[3:5])
        google_maps_url = loc_data[5]
        store.register_location(loc_id, city, address, lat, lng, google_maps_url)
