from datetime import timedelta

from cijenelib.models import ProductOffer
import operator
import re

# if we get 'æ', we need to decode as cp1250 instead of ansi!
# FIX_WEIRD_CHARS = str.maketrans({'È': 'Č', 'è': 'č', 'Æ': 'Ć', 'æ': 'ć'})
UA_HEADER = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36'}
DDMMYYYY_dots = re.compile(r'(\d{1,2})\.(\d{1,2})\.(\d{4})')
ONE_DAY = timedelta(days=1)
_ppu = operator.attrgetter('price_per_unit')
sublocations = {
    'Dubrovnik': {'Dubrovnik', },
    'Imotski': {'Imotski', },
    'Istra': {'Funtana', 'Poreč'},
    'Split': {'Split', 'Omiš', },
    'Omiš': {'Omiš', },
    'Poreč': {'Poreč'}
}



def stylize_unit_price(offer: ProductOffer, offers):
    min_price = _ppu(min(offers, key=_ppu))
    max_price = _ppu(max(offers, key=_ppu))
    if max_price != min_price:  # avoid division by zero
        t = 1 - (_ppu(offer) - min_price) / (max_price - min_price)
    else:
        t = 1.0
    # t is in [0, 1], smaller = more expensive
    # if t < 0.3 then hue=0, lightness linearly varies between 20% and 50%  (dark red to light red)
    # otherwise hue goes linearly between 0 and 120, lightness=50% (light red to light green)
    if t < 0.3:
        return f'background: hsla(0 100% {20+30*t/.3:.0f}/0.99); font-weight: {500+100*(t<.15)+100*(t<.75)}'
    return f'background: hsla({120*(t-0.3)/0.7:.0f} 100% 50%/0.99)'


def remove_extra_spaces(s: str) -> str:
    while '  ' in s:
        s = s.replace('  ', ' ')
    return s.strip()


def fix_price(price: str | float | None) -> float | None:
    if isinstance(price, str):
        price = price.strip()
    if price is None or price == '':  # avoid catching 0.0 here
        return None
    if isinstance(price, str):
        price = float('0' + price.replace(',', '.').replace('€', ''))
    return price


def most_occuring(s: str, *candidates: str) -> str:
    counts = {c: s.count(c) for c in candidates}
    return max(counts.items(), key=lambda x: x[1])[0]


def split_by_lengths(s: str, *lengths: int) -> list[str]:
    if sum(lengths) > len(s):
        raise ValueError('sum of lengths is greater than string length')
    parts = []
    for l in lengths:
        parts.append(s[:l])
        s = s[l:]
    if s:
        parts.append(s)
    return parts



def fix_address(address: str) -> str:
    address = address.strip().title()


    address = (address.replace('Zrtava', 'Žrtava')
               .replace('Fasizma', 'Fašizma')
               .replace('Inzenjerijske', 'Inženjerijske')
               .replace('V.Nazora', 'V. Nazora')
               .replace('3.Gardijske', '3. gardijske')  # bivša Gacka ulica u Osijeku
               .replace('rigade Kune', 'rigade „Kune“')
               .replace('Sporova', 'Šporova')
               .replace('Veliki Sor ', 'Veliki Šor ')
               .replace('Jelacica', 'Jelačića')
               .replace('Varazdinska', 'Varaždinska')
               .replace('Vl Nazora', 'Vladimira Nazora')
               .replace('103 brigade', '103. brigade')
               )

    for i in range(10):
        address = address.replace(f'Ul.{i}', f'ul. {i}')


    for t in {'Av.', 'Svibnja', 'Ulica', 'Na', 'Zona', 'Hrvatske', 'Trg', 'Javora', 'Žrtava',
              'Redarstvenika', 'Branitelja', 'Generala', 'Cesta', 'Naselje', 'Sabora', 'Grada',
              'Gardijske', 'Brigade', 'Put', 'Dr.', 'Doktora', 'Hrv.', 'Sveučilišta', 'Fašizma',
              'eliki Kraj', 'eliko Brdo', 'Dalmatinskih', 'Brigada', 'Magistrala', 'Vezna', 'I',
              'Inženjerijske Bojne', 'Avenija', 'Pape', 'Dr', 'Rata', 'Bana', 'Šetalište', 'Iz',
              'Preporoda', 'Odvojak', 'Pristanište', 'Zajednice', 'Kneza', 'Kralja', 'Jama',
              'U', 'Šor'}:
        t += ' '
        address = address.replace(t, t.lower())
    for t in {'Fkk', ' Hv', ' Ii', ' Ik', 'Vi ', 'Iii ', 'Ii ', 'Iv ', 'Viii ', 'Vii ', 'Ix ', 'Xii ', 'Xi '}:
        address = address.replace(t, t.upper())

    address = address.replace('hrvatske Republike', 'Hrvatske Republike')  # kad pise samo Republike onda je veliko R
    address = address.replace(' Bb', ' bb')
    if address.endswith('Iv'): address = address[:-2] + 'IV'
    if address[0].islower():
        address = address[0].upper() + address[1:]

    while '  ' in address:
        address = address.replace('  ', ' ')
    return address

CITIES = {
    'Biograd Na Moru': 'Biograd na Moru',
    'Cakovec': 'Čakovec',
    'Čatrnja Rakovica': 'Čatrnja',
    'Cavle': 'Čavle',
    'Cazma': 'Čazma',
    'Cepin': 'Čepin',
    'Dakovo': 'Đakovo',
    'Djakovo': 'Đakovo',
    'Durdevac': 'Đurđevac',
    'Fazana': 'Fažana',
    'Gospic': 'Gospić',
    'Grubisno Polje': 'Grubišno Polje',
    'Hum Na Sutli': 'Hum na Sutli',
    'Ivanic Grad': 'Ivanić-Grad',
    'Ivanić Grad': 'Ivanić-Grad',
    'Kastel Stafilic': 'Kaštel Štafilić',
    'Kastel Sucurac': 'Kaštel Sućurac',
    'Korcula': 'Korčula',
    'Krizevci': 'Križevci',
    'Malinska Krk': 'Malinska',
    'Metkovic': 'Metković',
    'Mursko Sredisce': 'Mursko Središće',
    'Nasice': 'Našice',
    'Nedescina': 'Nedešćina',
    'Nova Gradiska': 'Nova Gradiška',
    'Novigrad(Cittanova)': 'Novigrad',
    'Orebic': 'Orebić',
    'Otocac': 'Otočac',
    'Pakostane': 'Pakoštane',
    'Pasman': 'Pašman',
    'Pitomaca': 'Pitomača',
    'Ploce': 'Ploče',
    'Popovaca': 'Popovača',
    'Porec': 'Poreč',
    'Pozega': 'Požega',
    'Razine': 'Ražine',
    'Sibenik': 'Šibenik',
    'Šibenik-Ražine': 'Ražine',
    'Starigrad Paklenica': 'Starigrad',
    'Sukosan': 'Sukošan',
    'Sv. Ivan Zelina': 'Sveti Ivan Zelina',
    'Sv Ivan Zelina': 'Sveti Ivan Zelina',
    'Sv Kriz Zacretje': 'Sveti Križ Začretje',
    'Sveti Filip I Jakov': 'Sveti Filip i Jakov',
    'Trnovec Bartolovečki': 'Trnovec',
    'Umag-Umago': 'Umag',
    'Varazdin': 'Varaždin',
    'Varazdinske Toplice': 'Varaždinske Toplice',
    'Viskovo': 'Viškovo',
    'Zagreb - Sesvete': 'Zagreb-Sesvete',
    'Zagreb Dubec': 'Zagreb-Dubec',
    'Zagreb Novi Zagreb': 'Zagreb-Novi Zagreb',
    'Zapresic': 'Zaprešić',
    'Zminj': 'Žminj',
    'Zupanja': 'Županja',
}
def fix_city(city: str) -> str:
    city = city.strip().title()
    city = CITIES.get(city, city)
    return city