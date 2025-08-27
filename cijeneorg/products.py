from cijeneorg.models import Product

CocaCola = Product(id='cocacola', name='Coca Cola', unit='l')
CocaColaZero = Product(id='cocacolazero', name='Coca Cola Zero', unit='l')
Majoneza = Product(id='majoneza', name='Majoneza', unit='kg')

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
}
