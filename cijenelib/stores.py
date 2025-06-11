from cijenelib.models import Store
from cijenelib.fetchers import *

# noinspection SpellCheckingInspection
StoreLocations = {
    'konzum': {},
    'tommy': {},
    'spar': {},
    'studenac': {
        'T840': ['Dubrovnik', None, 'Vukovarska 26', 42.65162138382495, 18.09198514606226, 'https://maps.app.goo.gl/hjKaCQkvg2CKA2Az6'],
        'T598': ['Funtana', None, 'Bijela uvala 5', 45.18835835634874, 13.594310061224942, 'https://maps.app.goo.gl/ngj6eyDnjybyqJin8'],
        'T053': ['Imotski', None, 'Put Gaja 17', 43.44726239781231, 17.221914445681442, 'https://maps.app.goo.gl/7izEFZP3S8ofYxZn7'],
        'T100': ['Omiš', None, 'Četvrt Ribnjak 17', 43.44239334852886, 16.682653094297358, 'https://maps.app.goo.gl/ZBa5tPmnzJ5qefCf8'],
        'T127': ['Ploče', None, 'Plinjanska ul. 67', 43.05419399885792, 17.452332407818325, 'https://maps.app.goo.gl/4yCFxa8cm7QuA8RF6'],
        'T335': ['Cista Provo', None, 'Domovinskog rata 12A', 43.50279339148592, 16.94915036339688, 'https://maps.app.goo.gl/DviE9w1jJy4TSsF38'],
        'T544': ['Buzet', None, 'Trg Fontana 8/2', 45.40811919798952, 13.965747460607181, 'https://maps.app.goo.gl/1zoznrVA614yAJjC6'],
        'T779': ['Komiža', None, 'Put Batude 1A', 43.04607662990789, 16.091831419877007, 'https://maps.app.goo.gl/j42pJDXseZPyzFPf8'],
        'T783': ['Grohote', 'Otok Šolta', 'Podkuća 1', 43.39075421792372, 16.28541743226325, 'https://maps.app.goo.gl/YdN3jiM14J1f1noc9'],
        'T856': ['Slunj', None, 'Trg dr. Franje Tuđmana 1', 45.11439809539016, 15.585956476453264, 'https://maps.app.goo.gl/cyNqz6wRCFk3n1Xi7'],
        '1010': ['Kutina', None, 'Kolodvorska ulica 19', 45.47993275412257, 16.777660942214784, 'https://maps.app.goo.gl/HpKPLqeft2LXweNy5'],
        '1042': ['Popovača', None, 'Trg grofova Erdodyja 9', 45.57093189785281, 16.627999602164863, 'https://maps.app.goo.gl/axkzSmpBXLji9jMv8'],
        '1062': ['Petrinja', None, 'Ulica Josipa Nemeca 19', 45.438304703423164, 16.27172336300999, 'https://maps.app.goo.gl/SfDhKAoYv99JUNit7'],
        '1078': ['Sisak', None, 'Ulica Marijana Cvetkovića 12', 45.457518908125415, 16.388568215380303, 'https://maps.app.goo.gl/xt1bkyq2axVHjP9i8'],
        '1350': ['Sveti Križ Začretje', None, 'Ulica Ivana Kukuljevića Sakcinskog 12', 46.07732353256567, 15.906145146610415, 'https://maps.app.goo.gl/NfwqaBrsWszfPua26'],
        '1351': ['Pregrada', None, 'Obrtnička ulica 2', 46.16482534180408, 15.75142250834732, 'https://maps.app.goo.gl/3wonLViKv2aKQ3e27'],
        '1611': ['Jelsa', None, 'Jelsa 354', 43.16189807621674, 16.689109745408313, 'https://maps.app.goo.gl/2MobneKWVpnJknxW9'],
        'T993': ['Zaton', None, 'Dražnikova ulica 76T', 44.234274544248116, 15.165676847320366, 'https://maps.app.goo.gl/1XGU1zzRcQrJHvZq6']
    },
    'ribola': {
        '100': ['Kaštel Sućurac', None, 'Cesta dr. Franje Tuđmana 7', 43.539127224308366, 16.449687478781872, 'https://maps.app.goo.gl/45uB2i9RacrEb8rN8'],
        '096': ['Ploče', None, 'Obala dr. Franje Tuđmana 1', 43.05477584274801, 17.434607076349575, 'https://maps.app.goo.gl/8iTiBYJXAtduuxhF8'],
        '033': ['Kaštel Gomilica', None, 'Ul. Antuna Branka Šimića 21', 43.55054581945676, 16.40161969132508, 'https://maps.app.goo.gl/HHTvTwQ1CBanVY5J9'],
        '013': ['Trogir', None, 'Ul. Kardinala Alojzija Stepinca 41', 43.51876505976379, 16.24640453502216, 'https://maps.app.goo.gl/nzoLgMqZUCttgCm57'],
        '009': ['Kaštel Lukšić', None, 'Alojzija Stepinca 10',  43.55329706721916, 16.366780477387284, 'https://maps.app.goo.gl/ZpzU4nCHvxxHVVJHA'],
        '044': ['Okrug Gornji', None, 'Bana Josipa Jelačića 35', 43.49259838148869, 16.26337332861644, 'https://maps.app.goo.gl/96WqwmSZhEPPnujD6'],
        '030': ['Makarska', None, 'Breljanska ulica 1', 43.289731334256665, 17.026725368654517, 'https://maps.app.goo.gl/itfLXLWwQ3cDoeno7'],
        '078': ['Kaštel Stari', None, 'Cesta dr. Franje Tuđmana 705', 43.55324948718061, 16.344664006290095, 'https://maps.app.goo.gl/fRuVhVbeGX1JRT3s5'],
        '082': ['Kaštel Novi', None, 'Cesta dr. Franje Tuđmana 1108', 43.547565314862624, 16.322445884057355, 'https://maps.app.goo.gl/aTGU6ExSEMBuVvJJA'],
        '005': ['Kaštel Gomilica', None, 'Cesta dr. Franje Tuđmana 62', 43.54947744062817, 16.3961639091501, 'https://maps.app.goo.gl/hQqJK1vSDLAMpSQGA'],
        '054': ['Split', None, 'Ul. Dinka Šimunovića 16', 43.505794526159264, 16.474390889995348, 'https://maps.app.goo.gl/VR5SvcsRMnEKtFNA8'],
        '027': ['Sinj', None, 'Ul. Domovinskog rata 51', 43.70490025799626, 16.651233486207254, 'https://maps.app.goo.gl/hZ9XVkyswuFJs3XX9'],
        '028': ['Solin', None, 'Ul. dr. Martina Žižića 15', 43.54121546373953, 16.492842370842766, 'https://maps.app.goo.gl/wEMSg2LSf1uEXvF58'],
        '083': ['Orebić', None, 'Dubravica 13', 42.98382910153213, 17.198452560053752, 'https://maps.app.goo.gl/gU99qciqwswm3Ehz8'],
        '053': ['Split', None, 'Gat sv. Duje bb', 43.502959890938314, 16.44253935060138, 'https://maps.app.goo.gl/HLFTMzNSz1fYPvsq6'],
        '003': ['Kaštel Sućurac', None, 'Trg Gospojske Štrade 1', 43.545788712640345, 16.425408739726862, 'https://maps.app.goo.gl/nojHhsa2drsDCsUQ6'],
        '047': ['Split', None, 'Ul. Rikarda Katalinića Jeretova 12', 43.51116130569879, 16.472912717200277, 'https://maps.app.goo.gl/f1qiVTzUcyVG142t6'],
        '051': ['Split', None, 'Jobova ulica 1', 43.514445707208026, 16.430921326613905, 'https://maps.app.goo.gl/sV8R5MqsviE75qtr7'],
        '065': ['Split', None, 'Ul. kneza Mislava 2', 43.508753047860196, 16.443750031182358, 'https://maps.app.goo.gl/Xpooco1FuX7kkYQv5'],
        '080': ['Solin', None, 'Ul. kneza Trpimira 103', 43.54798734212575, 16.494248601963218, 'https://maps.app.goo.gl/p8GowHHbcMAeWWBm9'],
        '006': ['Kaštel Kambelovac', None, 'Ul. kralja Krešimira 1', 43.550308756048565, 16.385228826724216, 'https://maps.app.goo.gl/1xX1YXTATJPh7jye7'],
        '020': ['Solin', None, 'Ul. kralja Zvonimira 103', 43.53766849740367, 16.490903879703765, 'https://maps.app.goo.gl/T268n7asQ1RrahT5A'],
        '029': ['Trogir', None, 'Obala kralja Zvonimira 1', 43.5150677351588, 16.253378774581037, 'https://maps.app.goo.gl/e4UyYEbmoVSXofYCA'],
        '067': ['Split', None, 'Mažuranićevo šetalište 49-51', 43.51391327036177, 16.450873245800988, 'https://maps.app.goo.gl/AmHcrHnyLEMuT6LW6'],
        '068': ['Sinj', None, 'Ul. Miljenka Buljana 29', 43.70006024889549, 16.646963638700942, 'https://maps.app.goo.gl/scWWyaX9GsZkissq6'],
        '040': ['Makarska', None, 'Ul. Molizanskih Hrvata 20', 43.298976371953735, 17.019564892903652, 'https://maps.app.goo.gl/AvLMYEUT2kuDyvxG6'],
        '057': ['Split', None, 'Mostarska ul. 34', 43.523112555701026, 16.46801265440611, 'https://maps.app.goo.gl/zkkRakPZnce6iKS98'],
        '098': ['Dubrovnik', None, 'Obala Stjepana Radića 25', 42.65707853101532, 18.08934850057231, 'https://maps.app.goo.gl/DZM6UkaC7fzsvRbKA'],
        '023': ['Split', None, 'Poljička cesta 71', 43.51123595445364, 16.480075068107443, 'https://maps.app.goo.gl/JTffssc5Ta3G7cWe9'],
        '056': ['Split', None, 'Papandopulova ul. 7', 43.50757789421969, 16.47250041605867, 'https://maps.app.goo.gl/2ADSiHFSHf9vST7VA'],
        '014': ['Split', None, 'Plinarska ul. 14', 43.51082999564304, 16.436329630541294, 'https://maps.app.goo.gl/dvmJtQ9vAWLaCTcg6'],
        '037': ['Podstrana', None, 'Poljička cesta 94', 43.51486605614895, 16.541925153490048, 'https://maps.app.goo.gl/Bt2PFDxpHfng6RYV9'],
        '070': ['Dugi Rat', None, 'Poljička cesta 121a', 43.44520636957941, 16.638464014001872, 'https://maps.app.goo.gl/x5Zy6qoQcUzQxnap9'],
        '055': ['Split', None, 'Put Meja 6', 43.50518557236769, 16.427449998582873, 'https://maps.app.goo.gl/2vCVS7sCFp475mYe7'],
        '004': ['Kaštel Stari', None, 'Put Blata 2', 43.55201716806334, 16.339595022987805, 'https://maps.app.goo.gl/85rT6o8sQASnKSqSA'],
        '039': ['Kaštel Novi', None, 'Put sv. Jurja 115???', 43.56600985347082, 16.309372658337654, '/NE_MOGU_NAC_RIBOLU_039'],                          # TODO
        '095': ['Ražanj', None, 'Ražanj 95a', None, None, None],
        '010': ['Okrug Gornji', None, 'Stjepana Radića 51', None, None, None],
        '060': ['Nečujam', None, 'Nečujam bb', None, None, 'https://maps.app.goo.gl/uDFwJdhv2J41j1Rh6'],
        '052': ['Split', None, 'Ul. Ruđera Boškovića 10', 43.50559388745281, 16.466005794663978, 'https://maps.app.goo.gl/N8gwyPpM32JHPWxk7'],
        '074': ['Primošten', None, 'Splitska 22', 43.572051513860245, 15.940717834648607, 'https://maps.app.goo.gl/a9V4uh1Y3E9rfXRp8'],  # https://maps.app.goo.gl/B84dYT7stCfE5bK17 KAD POPRAVE
        '021': ['Split', None, 'Šibenska 59', 43.51926188772818, 16.45831167124054, 'https://maps.app.goo.gl/ZwBFnmTheqD75Y5F8'],
        '059': ['Jelsa', None, 'Strossmayerovo šetalište 1', 43.16194863281701, 16.689055212408846, 'https://maps.app.goo.gl/zz5nC14Qt7wSCHRU8'],
        '043': ['Podstrana', None, 'Strožanačka cesta 25', 43.501313864904404, 16.535291064939557, 'https://maps.app.goo.gl/XgAuUoR4vfX1WuYk6'],
        '017': ['Stobreč', None, 'Put sv. Lovre 45', 43.502638443479185, 16.52506748994115, 'https://maps.app.goo.gl/r4cAvDQpDCvJzM6f9'],
        '012': ['Podstrana', None, 'Cesta sv. Martina 11-13', 43.48220805442486, 16.55676130889109, 'https://maps.app.goo.gl/WNPFinrfSfUWdKT87'],
        '036': ['Trilj', None, 'Sv. Mihovila 57', 43.623359543410224, 16.71509890972567, 'https://maps.app.goo.gl/mnafUZMQUoSMiEpQ8'],
        '018': ['Seget Donji', None, 'Medena', 43.51329807378895, 16.20668777496156, 'https://maps.app.goo.gl/WnDEeCRhtJ8caStb9'],
        '075': ['Brela', None, 'Trg žrtava domovinskog rata', 43.37577124744275, 16.92467863850383, 'https://maps.app.goo.gl/NFL4HL21AdWbhiFs9'],
        '022': ['Šibenik', None, 'Ul. branitelja Domovinskog rata 4a', 43.724478080552004, 15.907291396112546, 'https://maps.app.goo.gl/CmxFr72inc5moq4G8'],
        '025': ['Šibenik', None, 'Ul. Stjepana Radića 77A', 43.732914245962014, 15.89724323645485, 'https://maps.app.goo.gl/t1mjddVdjeXYoHBj8'],
        '094': ['Zadar', None, 'Ul. Krste Odaka 5a', 44.11351746907505, 15.262489049090341, 'https://maps.app.goo.gl/KkN6Qe2Cr3QFhC9ZA'],
        '069': ['Makarska', None, 'Stari Velikobrdski put 39', 43.30375703603583, 17.017275221480205, 'https://maps.app.goo.gl/5z6gK2CbWL5jkhYv6'],
        '050': ['Split', None, 'Vinkovačka ul. 60', 43.51389369259432, 16.455025251407843, 'https://maps.app.goo.gl/7dXXE3xr3X4KMHiy6'],
        '034': ['Split', None, 'Vojka Krstulovića bb', 43.50674109236434, 16.453854364737666, 'https://maps.app.goo.gl/r3h3mpvtCvaLeAA79'],
        '049': ['Split', None, 'Vukovarska 131', 43.51435229100655, 16.469435409242916, 'https://maps.app.goo.gl/QFUJQsFa1egVaXri7'],
        '073': ['Kaštel Stari', None, 'Zagorski put 17', 43.56116824739413, 16.342755192246067, 'https://maps.app.goo.gl/Nfm2Py4iMzjoieh9A'],
        '061': ['Makarska', None, 'Zagrebačka ul. 50', 43.30576071845751, 17.011105195816416, 'https://maps.app.goo.gl/jmoVifVjb4bzH5qn6'],
        '092': ['Zadar', None, 'Ul. Miroslava Krleže 1a', 44.120548999243475, 15.228312191633433, 'https://maps.app.goo.gl/jfyX8ErEQrmrGgfq9'],
        '099': ['Dubrovnik', None, 'Žuljanska ul. 1', 42.65209558872317, 18.087602739040467, None]
    }
}

Tommy       = Store(name='Tommy',           url='https://www.tommy.hr/',    locations=StoreLocations['studenac'], fetch_prices=fetch_tommy_prices)
Konzum      = Store(name='Konzum',          url='https://www.konzum.hr/',   locations=StoreLocations['konzum'],   fetch_prices=fetch_konzum_prices)
Spar        = Store(name='Spar',            url='https://www.spar.hr/',     locations=StoreLocations['spar'],     fetch_prices=fetch_spar_prices)
Studenac    = Store(name='Studenac Market', url='https://www.studenac.hr/', locations=StoreLocations['studenac'], fetch_prices=fetch_studenac_prices, id='studenac')
Ribola      = Store(name='Ribola',          url='https://ribola.hr/',       locations=StoreLocations['ribola'],   fetch_prices=fetch_ribola_prices)
Lidl        = Store(name='Lidl',            url='https://www.lidl.hr/',     locations={}, fetch_prices=fetch_lidl_prices)
Plodine     = Store(name='Plodine',         url='https://www.plodine.hr/',  locations={}, fetch_prices=fetch_plodine_prices)
Eurospin    = Store(name='Eurospin',        url='https://www.eurospin.hr/', locations={}, fetch_prices=fetch_eurospin_prices)
Kaufland    = Store(name='Kaufland',        url='https://www.kaufland.hr/', locations={}, fetch_prices=fetch_kaufland_prices)
Metro       = Store(name='Metro',           url='https://www.metro-cc.hr/', locations={}, fetch_prices=fetch_metro_prices)
Boso        = Store(name='Boso',            url='https://www.boso.hr/',     locations={}, fetch_prices=fetch_boso_prices)
NTL         = Store(name='NTL',             url='https://www.ntl.hr/',      locations={}, fetch_prices=fetch_ntl_prices)
KTC         = Store(name='KTC',             url='https://www.ktc.hr/',      locations={}, fetch_prices=fetch_ktc_prices)
TrgovinaKrk = Store(name='Trgovina Krk',    url='https://trgovina-krk.hr/', locations={}, fetch_prices=fetch_trgovina_krk_prices)
Bakmaz      = Store(name='Bakmaz',          url='https://www.bakmaz.hr/',   locations={}, fetch_prices=fetch_bakmaz_prices)
DjeloVodice = Store(name='Djelo Vodice',    url='https://djelo-vodice.hr/', locations={}, fetch_prices=fetch_djelo_vodice_prices)
Djelo       = Store(name='Djelo',           url='https://djelo.hr/',        locations={}, fetch_prices=fetch_djelo_prices)
Zabac       = Store(name='Žabac Food Outlet', url='https://zabacfoodoutlet.hr/', locations={},  fetch_prices=fetch_zabac_prices, id='zabac')
Vrutak      = Store(name='Vrutak',          url='https://www.vrutak.hr/',        locations={},  fetch_prices=fetch_vrutak_prices)
Bure        = Store(name='Bure',            url='https://www.bure.hr/',          locations={},  fetch_prices=fetch_bure_prices)
Jadranka    = Store(name='Jadranka',        url='https://jadranka-trgovina.com/', locations={}, fetch_prices=fetch_jadranka_prices)
Trgocentar  = Store(name='Trgocentar',      url='https://trgocentar.com/',  locations={},       fetch_prices=fetch_trgocentar_prices)
Lorenco     = Store(name='Lorenco',         url='https://lorenco.hr/',      locations={},       fetch_prices=fetch_lorenco_prices)
Rotodinamic = Store(name='Roto dinamic',    url='https://www.rotodinamic.hr/', locations={},    fetch_prices=fetch_rotodinamic_prices)
Brodokomerc = Store(name='Brodokomerc',     url='http://brodokomerc.hr/', locations={},    fetch_prices=fetch_brodokomerc_prices)
Radenska    = Store(name='Radenska',        url='https://www.radenska.hr/', locations={},  fetch_prices=fetch_radenska_prices)