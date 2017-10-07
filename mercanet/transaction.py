"""
Classe qui représente et gère une transaction
"""
class Transaction:


   def __init__(self,amount,client,cart):
       """
       Initialise a transaction

       :param self:
       :param amount: Le montant de la transaction
       :param client: Le client qui effectue la transaction
       :param cart: Le panier du client
       :return:
       """
       self.amount = amount
       self.client = client
       self.cart = cart
       self.ID = 0 # @TODO: Compter le nombre de transaction et donner un ID en fonction
       self.state = 0

        #@TODO register Transaction in DB





