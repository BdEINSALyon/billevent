from django.db import models
import os
import sealTransaction
# Create your models here.

class TransactionMercanet(object):
    def __init__(self, amount, normalReturnUrl, transactionReference):
        self.amount = amount
        assert(amount != 0)
        self.currencyCode = 978
        self.interfaceVersion = os.environ['MERCANET_INTERFACE_VERSION']
        self.keyVersion = os.environ['MERCANET_KEY_VERSION']
        self.merchantId = os.environ['MERCANET_MERCHANT_ID']
        self.normalReturnUrl = normalReturnUrl
        self.orderChannel = "INTERNET"
        self.transactionReference = transactionReference
        self.Seal = sealTransaction(amount, interfaceVersion, merchantId, normalReturnUrl, transactionReference)
    seralizer_class = TransactionMercanetSerializer
#on ne hash pas la version de la clé ni l'algo utilisé (doc Mercanet)
