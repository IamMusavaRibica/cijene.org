from cijeneorg.models import Product

CocaCola = Product(id='cocacola', name='Coca Cola', unit='l')
CocaColaZero = Product(id='cocacolazero', name='Coca Cola Zero', unit='l')
Majoneza = Product(id='majoneza', name='Majoneza', unit='kg')

Margarin = Product(id='margarin', name='Margarin', unit='kg')

GaziranaVoda = Product(id='gaziranavoda', name='Gazirana voda', unit='l')
GaziranoPice = Product(id='gaziranopice', name='Gazirana pića', unit='l')

AllProducts = {
    # '3830065022566': [CocaCola, 0.33], # pepsi cola 0.33 l
    '5449000000286': [CocaCola, 2.0],  # classic 2 l
    '54491472': [CocaCola, 0.5],  # classic 0.5 l
    '5449000054227': [CocaCola, 1.0],  # classic 1 l
    '5449000131836': [CocaColaZero, 0.5],  # zero 0.5 l
    '5449000131843': [CocaColaZero, 2.0],  # zero 2 l
    '5449000133328': [CocaColaZero, 1.0],  # zero 1 l
    '5449000214911': [CocaCola, 0.33],  # classic 0.33 l
    '5449000059338': [CocaCola, 4.0],  # classic 2x2 l
    '5449000000439': [CocaCola, 1.5],  # classic 1.5 l
    '5449000247964': [CocaColaZero, 0.5],  # zero lemon 0.5 l
    '5449000133335': [CocaColaZero, 1.5],  # zero 1.5 l
    '5449000247988': [CocaColaZero, 1.0],  # zero lemon 1 l
    '5449000214799': [CocaColaZero, 0.33],  # zero 0.33 l
    '5000112652857': [CocaCola, 2.0],  # classic 6x0.33 l
    '5000112652871': [CocaColaZero, 2.0],  # zero 6x0.33 l
    '5449000034229': [CocaCola, 1.8],  # classic 12x150 ml
    '5449000138156': [CocaColaZero, 1.8],  # zero 12x150 ml
    '5449000195906': [CocaColaZero, 1.0],  # zero bez kofeina 1 l
    '5449000201935': [CocaColaZero, 0.5],  # zero bez kofeina 0.5 l
    '90338052': [CocaCola, 0.3],  # classic 0.3 l
    '5449000241085': [CocaCola, 0.9],  # classic 6x0.15 l
    '5449000241078': [CocaColaZero, 0.9],  # zero 6x0.15 l

    '3859888668188': [Majoneza, 0.62],  # Zvijezda

    # '3859888152113': [GaziranaVoda, 0.5],  # Jamnica
    # '3859888152014': [GaziranaVoda, 1.0],  # Jamnica
    # '3859888152045': [GaziranaVoda, 1.5],  # Jamnica

    '3858883228885': (Margarin, 0.250),  # Bakina Kuhinja
    '3858883227406': (Margarin, 0.500),  # Bakina Kuhinja
    '3858883221077': (Margarin, 0.250),  # Bakina Kuhinja
    '3856021223433': (Margarin, 0.250),  # S-BUDGET
    '3858882210102': (Margarin, 0.250),  # Zvijezda
    '3858882211611': (Margarin, 0.250),  # Zvijezda
    '3858882210553': (Margarin, 0.500),  # Zvijezda
    '3858882213677': (Margarin, 0.015),   # Margo
    '3850334268556': (Margarin, 0.500),  # K-Plus
    '3850334268532': (Margarin, 0.250),  # K-Plus
    '3856015314130': (Margarin, 0.300),  # Zvijezda TODO verify quantity
    '3856015301901': (Margarin, 0.250),  # Zvijezda
    '3858882211499': (Margarin, 20.0),# Zvijezda
    '3856015328625': (Margarin, 0.225),  # Omegol
    '3858882211420': (Margarin, 20.0), # Zvijezda
    '3856015305534': (Margarin, 0.250),
    '3856015323989': (Margarin, 1.0),
    '3858892943618': (Margarin, 0.250),
    '3856015309105': (Margarin, 0.500),
    '3856015317421': (Margarin, 0.250),
    '3858886938590': (Margarin, 0.250),
    '3856015317384': (Margarin, 0.250),
    '3856015327253': (Margarin, 0.400),
    '3856015332844': (Margarin, 0.225 + 0.2*0.225),  # TODO verify quantity
    '3856015327284': (Margarin, 0.225),
    '3858882210171': (Margarin, 0.500),
    '3858882210140': (Margarin, 0.250),


}
