from cijeneorg.models import Product


# Existing product pages
CocaCola = Product(id='cocacola', name='Coca Cola', unit='l')
CocaColaZero = Product(id='cocacolazero', name='Coca Cola Zero', unit='l')
Majoneza = Product(id='majoneza', name='Majoneza', unit='kg')
RmzAutic = Product(id='rmzautic', name='RMZ Autić', unit='kom')
Margarin = Product(id='margarin', name='Margarin', unit='kg')

# Common products stocked by Žabac. Flavor and formula variants intentionally
# have separate pages; package sizes of the same product share a page.
Jamnica = Product(id='jamnica', name='Jamnica', unit='l')
JanaLedeniCajBreskva = Product(id='janaledenicajbreskva', name='Jana ledeni čaj breskva', unit='l')
DukatosJagoda = Product(id='dukatosjagoda', name='Dukatos jogurt jagoda', unit='kg')
DukatosNatur = Product(id='dukatosnatur', name='Dukatos jogurt natur', unit='kg')
Vegeta = Product(id='vegeta', name='Vegeta', unit='kg')
LikviUltraFresh = Product(id='likviultrafresh', name='Likvi Ultra Fresh', unit='l')
JanaVitaminImmunoLimun = Product(
    id='janavitaminimmunolimun', name='Jana Vitamin Immuno limun', unit='l'
)
JanaVitaminHappyNaranca = Product(
    id='janavitaminhappynaranca', name='Jana Vitamin Happy naranča', unit='l'
)
FantaOrange = Product(id='fantaorange', name='Fanta Orange', unit='l')
Sprite = Product(id='sprite', name='Sprite', unit='l')
ArfCreamCitro = Product(id='arfcreamcitro', name='Arf Cream Citro', unit='l')
BAktivLGGNatur = Product(id='baktivlggnatur', name='b.Aktiv LGG natur', unit='kg')
DukatosBademPistacija = Product(
    id='dukatosbadempistacija', name='Dukatos jogurt badem i pistacija', unit='kg'
)
PodravkaDzemMarelica = Product(
    id='podravkadzemmarelica', name='Podravka džem marelica', unit='kg'
)
GavrilovicMesniDorucak = Product(
    id='gavrilovicmesnidorucak', name='Gavrilović mesni doručak', unit='kg'
)
PodravkaKoncentratRajcice = Product(
    id='podravkakoncentratrajcice', name='Podravka koncentrat rajčice', unit='kg'
)
KrasBananko = Product(id='krasbananko', name='Kraš Bananko', unit='kg')
OrbitBlueberry = Product(id='orbitblueberry', name='Orbit Blueberry', unit='kg')
OrbitSweetMint = Product(id='orbitsweetmint', name='Orbit Sweet Mint', unit='kg')
VindijaPudingVanilija = Product(
    id='vindijapudingvanilija', name='Vindija puding vanilija', unit='kg'
)
Raffaello = Product(id='raffaello', name='Raffaello', unit='kg')
OrbitSpearmint = Product(id='orbitspearmint', name='Orbit Spearmint', unit='kg')
JanaJagodaGuava = Product(id='janajagodaguava', name='Jana jagoda i guava', unit='l')
JanaLimunLimeta = Product(id='janalimunlimeta', name='Jana limun i limeta', unit='l')
PodravkaAjvarBlagi = Product(
    id='podravkaajvarblagi', name='Podravka ajvar blagi', unit='kg'
)
KrasFrondiNougat = Product(id='krasfrondinougat', name='Kraš Frondi nougat', unit='kg')
GavrilovicJetrenaPasteta = Product(
    id='gavrilovicjetrenapasteta', name='Gavrilović jetrena pašteta', unit='kg'
)
HellIceCoffeeLatte = Product(
    id='hellicecoffeelatte', name='Hell Ice Coffee Latte', unit='l'
)
MilkaNoisette = Product(id='milkanoisette', name='Milka Noisette', unit='kg')
PikMortadela = Product(id='pikmortadela', name='PIK mortadela', unit='kg')
OrbitBubblemint = Product(id='orbitbubblemint', name='Orbit Bubblemint', unit='kg')
Ozujsko = Product(id='ozujsko', name='Ožujsko', unit='l')
KrasPeppermint = Product(id='kraspepermint', name='Kraš Peppermint', unit='kg')
PresidentMladiKajmak = Product(
    id='presidentmladikajmak', name='President mladi kajmak', unit='kg'
)
SaltasStapiciKikiriki = Product(
    id='saltaskikiriki', name='Koestlin Saltas štapići s kikirikijem', unit='kg'
)
SaltasSlaniStapici = Product(
    id='saltasslanistapici', name='Koestlin Saltas slani štapići', unit='kg'
)
ZvijezdaTartar = Product(id='zvijezdatartar', name='Zvijezda tartar', unit='kg')
TucBacon = Product(id='tucbacon', name='TUC Bacon', unit='kg')
TucOriginal = Product(id='tucoriginal', name='TUC Original', unit='kg')
GavrilovicCajnaPasteta = Product(
    id='gavriloviccajnapasteta', name='Gavrilović čajna pašteta', unit='kg'
)
JanaVitaminRefresh = Product(
    id='janavitaminrefresh', name='Jana Vitamin Refresh menta i limeta', unit='l'
)
PodravkaAjvarLjuti = Product(
    id='podravkaajvarljuti', name='Podravka ajvar ljuti', unit='kg'
)
AlproAlmondRoasted = Product(
    id='alproalmondroasted', name='Alpro Almond Roasted', unit='l'
)
KrasKikiTuttiFrutti = Product(
    id='kraskikituttifrutti', name='Kraš Kiki Tutti Frutti', unit='kg'
)
BountyMilk = Product(id='bountymilk', name='Bounty Milk', unit='kg')
LedoBrokula = Product(id='ledobrokula', name='Ledo brokula', unit='kg')
DolcelaPrasakZaPecivo = Product(
    id='dolcelaprasakzapecivo', name='Dolcela prašak za pecivo', unit='kg'
)
DukatTrajnoMlijeko28 = Product(
    id='dukattrajnomlijeko28', name='Dukat trajno mlijeko 2,8%', unit='l'
)
DukatKiseloVrhnje12 = Product(
    id='dukatkiselovrhnje12', name='Dukat kiselo vrhnje 12%', unit='kg'
)
PodravkaGulas = Product(id='podravkagulas', name='Podravka goveđi gulaš', unit='kg')
HellClassic = Product(id='hellclassic', name='Hell Classic', unit='l')
HidraIso = Product(id='hidraiso', name='Hidra ISO', unit='l')
JamnicaLimunada = Product(id='jamnicalimunada', name='Jamnica Limunada', unit='l')
JamnicaNarancada = Product(id='jamnicanarancada', name='Jamnica Narančada', unit='l')
KalodontExtraClean = Product(
    id='kalodontextraclean', name='Kalodont Extra Clean', unit='l'
)
LedoKingDouble = Product(id='ledokingdouble', name='Ledo King Double', unit='l')
PikKuhanaSunka = Product(id='pikkuhanasunka', name='PIK kuhana šunka', unit='kg')
LahorSensitive = Product(id='lahorsensitive', name='Lahor Sensitive', unit='kg')
LedoMachoVanilla = Product(id='ledomachovanilla', name='Ledo Macho Vanilla', unit='l')
LedoFrancuskaSalata = Product(
    id='ledofrancuskasalata', name='Ledo mix za francusku salatu', unit='kg'
)
Nescafe3in1Classic = Product(
    id='nescafe3in1classic', name='Nescafé 3in1 Classic', unit='kg'
)
OrbitPeppermint = Product(id='orbitpeppermint', name='Orbit Peppermint', unit='kg')
MaraskaPelinkovac = Product(id='maraskapelinkovac', name='Maraska Pelinkovac', unit='l')
PodravkaPudingCokolada = Product(
    id='podravkapudingcokolada', name='Podravka puding čokolada', unit='kg'
)
VindijaProteinPudingKokosBadem = Product(
    id='vindijaproteinpudingkokosbadem',
    name='Vindija Protein puding kokos-badem',
    unit='kg',
)
KanditRikiRizaCokolada = Product(
    id='kanditrikirizacokolada', name='Kandit Riki riža čokolada', unit='kg'
)
TucCheese = Product(id='tuccheese', name='TUC Cheese', unit='kg')
XixoIceTeaBreskva = Product(
    id='xixoiceteabreskva', name='XIXO Ice Tea Breskva', unit='l'
)
PodravkaZapeceniGrah = Product(
    id='podravkazapecenigrah', name='Podravka zapečeni grah', unit='kg'
)
ChioCipiCipsPaprika = Product(
    id='chiocipicipspaprika', name='Chio Čipi Čips paprika', unit='kg'
)
KrasCoksaCreamyMilk = Product(
    id='krascoksacreamymilk', name='Kraš Čoksa Creamy Milk', unit='kg'
)
LedoSlagCasica = Product(id='ledoslagcasica', name='Ledo šlag u čašici', unit='l')
KinderBueno = Product(id='kinderbueno', name='Kinder Bueno', unit='kg')
KinderBuenoWhite = Product(id='kinderbuenowhite', name='Kinder Bueno White', unit='kg')
Nutella = Product(id='nutella', name='Nutella', unit='kg')
NiveaCreme = Product(id='niveacreme', name='Nivea Creme', unit='l')

# Overall cross-chain leaders not currently stocked by Žabac, plus size
# variants which share pages with Žabac products above.
NilaHappyColors = Product(id='nilahappycolors', name='Nila Happy Colors', unit='l')
ArfDeobad = Product(id='arfdeobad', name='Arf Deobad', unit='l')
ArfCreamOriginal = Product(id='arfcreamoriginal', name='Arf Cream Original', unit='l')
SuperJonStaklo = Product(
    id='superjonstaklo', name='Super Jon Staklo Alkohol & Ocat', unit='l'
)
SanitarStrong = Product(id='sanitarstrong', name='Sanitar Strong', unit='l')
BadelAntiquePelinkovac = Product(
    id='badelantiquepelinkovac', name='Badel Antique Pelinkovac', unit='l'
)
CedevitaFreshLimun = Product(
    id='cedevitafreshlimun', name='Cedevita Fresh Limun', unit='l'
)
CedevitaFreshNaranca = Product(
    id='cedevitafreshnaranca', name='Cedevita Fresh Naranča', unit='l'
)
CedevitaLimun = Product(id='cedevitalimun', name='Cedevita Limun', unit='kg')
CedevitaNaranca = Product(id='cedevitanaranca', name='Cedevita Naranča', unit='kg')
BAktivSmoothieBorovnicaBanana = Product(
    id='baktivsmoothieborovnicabanana',
    name='b.Aktiv smoothie borovnica-banana',
    unit='kg',
)
BAktivSmoothieJagodaAnanas = Product(
    id='baktivsmoothiejagodaananas', name='b.Aktiv smoothie jagoda-ananas', unit='kg'
)
DukatTekuciJogurt = Product(
    id='dukattekucijogurt', name='Dukat tekući jogurt 2,8%', unit='l'
)
DukatVocniJogurtJagoda = Product(
    id='dukatvocnijogurtjagoda', name='Dukat voćni jogurt jagoda', unit='kg'
)
DukatLaganoJutroMlijeko = Product(
    id='dukatlaganojutromlijeko', name='Dukat Lagano jutro mlijeko', unit='l'
)
JanaLedeniCajSumskoVoce = Product(
    id='janaledenicajsumsko', name='Jana ledeni čaj šumsko voće i brusnica', unit='l'
)


# A few retailers reuse the same GTIN for a consumer unit and an outer/promo
# pack. Keep the normal mapping below as the default and override only the
# store whose current price list clearly sells a different total quantity.
ProductQuantityOverrides = {
    ('3856015314130', 'lidl'): 0.25,
    ('3856015332844', 'lidl'): 0.225,
    ('8000500106860', 'metro'): 0.9,
}


AllProducts = {
    '4895065044894': (RmzAutic, 1),

    # Coca Cola
    '5449000000286': (CocaCola, 2.0),
    '54491472': (CocaCola, 0.5),
    '5449000054227': (CocaCola, 1.0),
    '5449000131836': (CocaColaZero, 0.5),
    '5449000131843': (CocaColaZero, 2.0),
    '5449000133328': (CocaColaZero, 1.0),
    '5449000214911': (CocaCola, 0.33),
    '5449000059338': (CocaCola, 4.0),
    '5449000000439': (CocaCola, 1.5),
    '5449000247964': (CocaColaZero, 0.5),
    '5449000133335': (CocaColaZero, 1.5),
    '5449000247988': (CocaColaZero, 1.0),
    '5449000214799': (CocaColaZero, 0.33),
    '5000112652857': (CocaCola, 2.0),
    '5000112652871': (CocaColaZero, 2.0),
    '5449000034229': (CocaCola, 1.8),
    '5449000138156': (CocaColaZero, 1.8),
    '5449000195906': (CocaColaZero, 1.0),
    '5449000201935': (CocaColaZero, 0.5),
    '90338052': (CocaCola, 0.3),
    '5449000241085': (CocaCola, 0.9),
    '5449000241078': (CocaColaZero, 0.9),

    '3859888668188': (Majoneza, 0.62),

    # Water, soft drinks, coffee and alcoholic drinks
    '3859888152038': (Jamnica, 0.25),
    '3859888152113': (Jamnica, 0.5),
    '3859888152021': (Jamnica, 0.5),
    '3859888152663': (Jamnica, 0.75),
    '3859888152014': (Jamnica, 1.0),
    '3858890873054': (Jamnica, 1.0),
    '3859888152045': (Jamnica, 1.5),
    '3856028503262': (Jamnica, 1.5),
    '3858884601052': (JanaLedeniCajBreskva, 0.5),
    '3858884601045': (JanaLedeniCajBreskva, 1.5),
    '3858884601731': (JanaLedeniCajSumskoVoce, 0.5),
    '3858884601717': (JanaLedeniCajSumskoVoce, 1.5),
    '3858884600956': (JanaJagodaGuava, 0.5),
    '3858884600871': (JanaJagodaGuava, 1.5),
    '3858884600932': (JanaLimunLimeta, 0.5),
    '3858884600819': (JanaLimunLimeta, 1.5),
    '3858890871975': (JanaVitaminImmunoLimun, 0.5),
    '3858890873085': (JanaVitaminImmunoLimun, 1.5),
    '3858890874013': (JanaVitaminHappyNaranca, 0.5),
    '3858890874044': (JanaVitaminHappyNaranca, 1.5),
    '3856028501305': (JanaVitaminHappyNaranca, 1.5),
    '3856028501480': (JanaVitaminRefresh, 0.5),
    '3858890874570': (JanaVitaminRefresh, 0.5),
    '3858890874686': (JanaVitaminRefresh, 1.5),
    '5449000322142': (FantaOrange, 0.5),
    '5449000322180': (FantaOrange, 1.0),
    '5449000322166': (FantaOrange, 1.5),
    '5449000322203': (FantaOrange, 2.0),
    '5449000322241': (FantaOrange, 0.33),
    '54026476': (FantaOrange, 0.3),
    '54023840': (FantaOrange, 0.25),
    '5449000322326': (FantaOrange, 4.0),
    '5000112669046': (FantaOrange, 2.0),
    '40822938': (FantaOrange, 0.5),
    '5449000004840': (FantaOrange, 2.0),
    '5449000322227': (FantaOrange, 0.25),
    '5449000006271': (FantaOrange, 1.0),
    '5449000011527': (FantaOrange, 0.33),
    '5449000000712': (FantaOrange, 0.25),
    '5449000059390': (FantaOrange, 4.0),
    '5000112625172': (FantaOrange, 1.5),
    '5449000054531': (FantaOrange, 0.33),
    '5000112683073': (FantaOrange, 0.33),
    '5000112654035': (FantaOrange, 0.33),
    '5449000016669': (FantaOrange, 2.0),
    # Metro outer-carton GTINs (the product names only state bottle size).
    '5449000322159': (FantaOrange, 6.0),
    '5000112669060': (FantaOrange, 0.33),
    '5449000322210': (FantaOrange, 12.0),
    '5449000322258': (FantaOrange, 7.92),
    '5449000322197': (FantaOrange, 12.0),
    '5449000053527': (FantaOrange, 1.5),
    '5449000006011': (FantaOrange, 2.0),
    '5000112531121': (FantaOrange, 2.0),
    '5000112530117': (FantaOrange, 0.25),
    '5449000052926': (FantaOrange, 1.5),
    '5449000322265': (FantaOrange, 6.0),
    '5449000334992': (Sprite, 0.5),
    '5449000335012': (Sprite, 1.0),
    '5449000335036': (Sprite, 2.0),
    '5449000349491': (Sprite, 0.33),
    '54031807': (Sprite, 0.25),
    '5449000004864': (Sprite, 2.0),
    '54491069': (Sprite, 0.5),
    '5449000050939': (Sprite, 1.0),
    '54490970': (Sprite, 0.25),
    '5449000349507': (Sprite, 0.33),
    # Metro outer-carton GTINs.
    '5449000335005': (Sprite, 6.0),
    '5449000017734': (Sprite, 2.0),
    '5449000110671': (Sprite, 0.5),
    '5449000335050': (Sprite, 6.0),
    '5449000335029': (Sprite, 12.0),
    '5449000335043': (Sprite, 12.0),
    '5449000000729': (Sprite, 0.25),
    '5000112683059': (Sprite, 0.33),
    '5449000108258': (Sprite, 0.33),
    '5999860497073': (HellIceCoffeeLatte, 0.25),
    '5999884034469': (HellClassic, 0.25),
    '5999884034209': (HellClassic, 0.5),
    '3850131005118': (HidraIso, 0.5),
    '3850131006283': (HidraIso, 2.0),
    '3856028506065': (JamnicaLimunada, 0.33),
    '3856028502135': (JamnicaLimunada, 0.5),
    '3856028506096': (JamnicaNarancada, 0.33),
    '8445291259331': (Nescafe3in1Classic, 0.0155),
    '5941017016354': (Nescafe3in1Classic, 0.0165),
    '8445291261044': (Nescafe3in1Classic, 0.155),
    '7613036842365': (Nescafe3in1Classic, 0.165),
    '8445291956315': (Nescafe3in1Classic, 0.434),
    '3850131400609': (Ozujsko, 0.5),
    '3850131001608': (Ozujsko, 2.0),
    '3850131986011': (Ozujsko, 2.0),
    '3850158406301': (MaraskaPelinkovac, 0.1),
    '3850112110572': (BadelAntiquePelinkovac, 0.7),
    '3850322013380': (CedevitaFreshLimun, 0.34),
    '3850322013366': (CedevitaFreshNaranca, 0.34),
    '3850322015001': (CedevitaLimun, 0.9),
    '3850322014981': (CedevitaNaranca, 0.9),
    '5411188110835': (AlproAlmondRoasted, 1.0),
    '5999885747085': (XixoIceTeaBreskva, 0.25),

    # Dairy and frozen products
    '3850354009788': (DukatosJagoda, 0.15),
    '3850354009726': (DukatosNatur, 0.15),
    '3850354009764': (DukatosBademPistacija, 0.15),
    '3850354015833': (BAktivLGGNatur, 0.33),
    '3850354015819': (BAktivLGGNatur, 1.0),
    '3850354015888': (BAktivSmoothieBorovnicaBanana, 0.33),
    '3850354015901': (BAktivSmoothieJagodaAnanas, 0.33),
    '3850354016021': (DukatTekuciJogurt, 1.0),
    '3850354016038': (DukatTekuciJogurt, 1.5),
    '3850354000921': (DukatTekuciJogurt, 0.18),
    '3850354016007': (DukatTekuciJogurt, 0.33),
    '3850354016014': (DukatTekuciJogurt, 0.5),
    '3850354016649': (DukatTekuciJogurt, 1.0),
    '3850354000938': (DukatTekuciJogurt, 0.18),
    '3850354018858': (DukatTekuciJogurt, 0.33),
    '3850354001010': (DukatTekuciJogurt, 1.0),
    '3850354000983': (DukatTekuciJogurt, 0.5),
    '3850354009184': (DukatTekuciJogurt, 0.23),
    '3850354016045': (DukatVocniJogurtJagoda, 1.0),
    '3850354017103': (DukatLaganoJutroMlijeko, 1.0),
    '3850354016830': (DukatTrajnoMlijeko28, 1.0),
    '3850354006053': (DukatTrajnoMlijeko28, 1.0),
    '3850354006077': (DukatTrajnoMlijeko28, 8.0),
    '3850354006817': (DukatTrajnoMlijeko28, 0.5),
    '3850354005247': (DukatTrajnoMlijeko28, 0.2),
    '3850354016847': (DukatTrajnoMlijeko28, 1.0),
    '3850354005254': (DukatTrajnoMlijeko28, 0.2),
    '3850354006824': (DukatTrajnoMlijeko28, 0.5),
    '3850354009863': (DukatKiseloVrhnje12, 0.9),
    '3850354002024': (DukatKiseloVrhnje12, 0.2),
    '3850354000471': (DukatKiseloVrhnje12, 0.4),
    '3850354006336': (DukatKiseloVrhnje12, 0.6),
    '3850153003192': (DukatKiseloVrhnje12, 0.2),
    '3850354009702': (DukatKiseloVrhnje12, 0.2),
    '3870311000733': (DukatKiseloVrhnje12, 0.9),
    '3858883520323': (DukatKiseloVrhnje12, 0.2),
    '38500022': (VindijaPudingVanilija, 0.125),
    '3850108040920': (VindijaProteinPudingKokosBadem, 0.18),
    '3850116053103': (LedoBrokula, 0.4),
    '3850116756028': (LedoBrokula, 0.45),
    '3850116053493': (LedoFrancuskaSalata, 0.4),
    '3850116037165': (LedoKingDouble, 0.1),
    '3850116102627': (LedoKingDouble, 0.3),
    '3850116641942': (LedoMachoVanilla, 0.075),
    '3850116506623': (LedoSlagCasica, 0.22),

    # Savoury food, spreads and seasonings
    '3850104008054': (Vegeta, 0.075),
    '3850104008825': (Vegeta, 0.125),
    '3850104008597': (Vegeta, 0.25),
    '3850104216466': (Vegeta, 0.3),
    '3850104047046': (Vegeta, 1.0),
    '3856020252502': (PodravkaDzemMarelica, 0.67),
    '3858881220010': (GavrilovicMesniDorucak, 0.15),
    '3850104053214': (PodravkaKoncentratRajcice, 0.12),
    '3850104053221': (PodravkaKoncentratRajcice, 0.19),
    '3850104268533': (PodravkaKoncentratRajcice, 0.3),
    '3856020269166': (PodravkaKoncentratRajcice, 0.37),
    '3856020269197': (PodravkaKoncentratRajcice, 0.72),
    '3850104022517': (PodravkaAjvarBlagi, 0.195),
    '3856020233617': (PodravkaAjvarBlagi, 0.31),
    '3850104051029': (PodravkaAjvarBlagi, 0.35),
    '3850104051012': (PodravkaAjvarBlagi, 0.69),
    '3856020233679': (PodravkaAjvarLjuti, 0.31),
    '3850104050565': (PodravkaAjvarLjuti, 0.35),
    '3850104050572': (PodravkaAjvarLjuti, 0.69),
    '3856020260712': (PodravkaAjvarLjuti, 0.95),
    '3858881221543': (GavrilovicJetrenaPasteta, 0.1),
    '3858881221529': (GavrilovicCajnaPasteta, 0.1),
    '3850139171044': (PikMortadela, 0.15),
    '3850139360516': (PikKuhanaSunka, 0.125),
    '8606002110895': (PresidentMladiKajmak, 0.25),
    '8606002112684': (PresidentMladiKajmak, 0.1),
    '3856015328441': (ZvijezdaTartar, 0.26),
    '3858882214940': (ZvijezdaTartar, 0.165),
    '3858882216296': (ZvijezdaTartar, 2.0),
    '3850104020087': (PodravkaGulas, 0.4),
    '3850104035739': (PodravkaZapeceniGrah, 0.4),

    # Biscuits, confectionery and snacks
    '3850102127252': (KrasBananko, 0.03),
    '42123880': (OrbitBlueberry, 0.014),
    '50173808': (OrbitSweetMint, 0.014),
    '50173822': (OrbitSpearmint, 0.014),
    '42247371': (OrbitBubblemint, 0.014),
    '50173204': (OrbitPeppermint, 0.014),
    '5413548040639': (Raffaello, 0.04),
    '4008400185521': (Raffaello, 0.04),
    '8000500164242': (Raffaello, 0.07),
    '8000500311585': (Raffaello, 0.08),
    '8000500359556': (Raffaello, 0.09),
    '4008400183022': (Raffaello, 0.23),
    '3850102002221': (KrasFrondiNougat, 0.25),
    '7622210043955': (MilkaNoisette, 0.08),
    '7622202269097': (MilkaNoisette, 0.09),
    '7622202257674': (MilkaNoisette, 0.25),
    '3850102210312': (KrasPeppermint, 0.1),
    '3856014114359': (SaltasStapiciKikiriki, 0.04),
    '3856014114205': (SaltasStapiciKikiriki, 0.16),
    '3856014107078': (SaltasStapiciKikiriki, 0.27),
    '3856014112881': (SaltasSlaniStapici, 0.045),
    '3856014117275': (SaltasSlaniStapici, 0.09),
    '3856014112850': (SaltasSlaniStapici, 0.22),
    '7622300570293': (TucBacon, 0.1),
    '6194008556226': (TucOriginal, 0.08),
    '5410041435702': (TucOriginal, 0.1),
    '5998711388928': (TucCheese, 0.1),
    '3850102516704': (KrasKikiTuttiFrutti, 0.1),
    '5000159557771': (BountyMilk, 0.057),
    '5000159562508': (BountyMilk, 0.227),
    '3850104242175': (DolcelaPrasakZaPecivo, 0.072),
    '3856020275501': (DolcelaPrasakZaPecivo, 0.072),
    '3850104274817': (PodravkaPudingCokolada, 0.045),
    '3856024800679': (KanditRikiRizaCokolada, 0.075),
    '3858881040458': (KanditRikiRizaCokolada, 0.2),
    '3856021305702': (ChioCipiCipsPaprika, 0.055),
    '3856021306549': (ChioCipiCipsPaprika, 0.12),
    '3850102001613': (KrasCoksaCreamyMilk, 0.068),
    '80052760': (KinderBueno, 0.043),
    '4008400320328': (KinderBueno, 0.129),
    '8000500383056': (KinderBueno, 0.1075),
    '5020411113828': (KinderBueno, 0.172),
    '8000500073698': (KinderBueno, 0.043),
    '4008400322728': (KinderBueno, 0.129),
    '3858894681969': (KinderBueno, 0.28),
    '5905408022010': (KinderBueno, 0.344),
    '8000500121436': (KinderBuenoWhite, 0.117),
    '80761761': (KinderBuenoWhite, 0.039),
    '8000500394694': (KinderBuenoWhite, 0.0975),
    '80051220': (KinderBuenoWhite, 0.039),
    '8000500121467': (KinderBuenoWhite, 0.039),
    '8000500075784': (KinderBuenoWhite, 0.312),
    '80135876': (Nutella, 0.4),
    '80176800': (Nutella, 0.75),
    '8000500179864': (Nutella, 0.6),
    '8000500082379': (Nutella, 1.0),
    '80895237': (Nutella, 0.7),
    '8000500131329': (Nutella, 3.0),
    '59032823': (Nutella, 0.63),
    '8000500106860': (Nutella, 0.015),
    '8000500166819': (Nutella, 1.0),
    '80052395': (Nutella, 0.4),
    '4008400401829': (Nutella, 1.0),
    '4008400404127': (Nutella, 0.75),

    # Household and personal care
    '3850105170101': (LikviUltraFresh, 0.45),
    '3850105170286': (LikviUltraFresh, 0.9),
    '3850105170330': (LikviUltraFresh, 1.35),
    '3850105169518': (NilaHappyColors, 0.9),
    '3850105169662': (NilaHappyColors, 2.7),
    '3850105181596': (ArfCreamCitro, 0.4),
    '3850105181190': (ArfDeobad, 0.65),
    '3850105181626': (ArfCreamOriginal, 0.4),
    '3850111503382': (SuperJonStaklo, 0.65),
    '3850111503399': (SanitarStrong, 0.65),
    '3850105143006': (KalodontExtraClean, 0.075),
    '3850105176950': (LahorSensitive, 0.08),
    '4005808158041': (NiveaCreme, 0.25),
    '4005808157983': (NiveaCreme, 0.15),
    '42163176': (NiveaCreme, 0.075),
    '42158486': (NiveaCreme, 0.03),
    '4005808158096': (NiveaCreme, 0.4),
    '4005808801039': (NiveaCreme, 0.075),
    '4005808801046': (NiveaCreme, 0.15),
    '3850114500449': (NiveaCreme, 0.15),
    '4005800001192': (NiveaCreme, 0.15),
    '5900017304007': (NiveaCreme, 0.05),
    '42163145': (NiveaCreme, 0.075),
    '4005808801053': (NiveaCreme, 0.25),

    # Margarine variants retained from the original product list
    '3858883228885': (Margarin, 0.250),
    '3858883227406': (Margarin, 0.500),
    '3858883221077': (Margarin, 0.250),
    '3856021223433': (Margarin, 0.250),
    '3858882210102': (Margarin, 0.250),
    '3858882211611': (Margarin, 0.250),
    '3858882210553': (Margarin, 0.500),
    '3858882213677': (Margarin, 0.015),
    '3850334268556': (Margarin, 0.500),
    '3850334268532': (Margarin, 0.250),
    '3856015314130': (Margarin, 0.300),
    '3856015301901': (Margarin, 0.250),
    '3858882211499': (Margarin, 20.0),
    '3856015328625': (Margarin, 0.225),
    '3858882211420': (Margarin, 20.0),
    '3856015305534': (Margarin, 0.250),
    '3856015323989': (Margarin, 1.0),
    '3858892943618': (Margarin, 0.250),
    '3856015309105': (Margarin, 0.500),
    '3856015317421': (Margarin, 0.250),
    '3858886938590': (Margarin, 0.250),
    '3856015317384': (Margarin, 0.250),
    '3856015327253': (Margarin, 0.400),
    '3856015332844': (Margarin, 0.225 + 0.2 * 0.225),
    '3856015327284': (Margarin, 0.225),
    '3858882210171': (Margarin, 0.500),
    '3858882210140': (Margarin, 0.250),
}
