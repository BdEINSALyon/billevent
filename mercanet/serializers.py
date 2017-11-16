from rest_framework import serializers
from models import TransactionMercanet
from mercanet import sealTransaction

secretKey = os.environ['MERCANET_SECRET_KEY']


class TransactionMercanetSerializer(serializers.Serializer):
    class Meta:
        model = TransactionMercanet
        fields = ('amount', 'currencyCode', 'interfaceVersion', 'keyVersion', 'merchantID', 'normalReturnUrl',
                  'transactionReference', 'Seal')

        def create(self):
            TransactionMercanet.Seal = sealTransaction(TransactionMercanet.amount, TransactionMercanet.currencyCode,
                                                       TransactionMercanet.interfaceVersion,
                                                       TransactionMercanet.keyVersion, TransactionMercanet.merchantId,
                                                       TransactionMercanet.normalReturnUrl,
                                                       TransactionMercanet.orderChannel,
                                                       TransactionMercanet.transactionReference, secretKey)
            return

        # comment peut-on ajouter le seal à ce serializer ? il faut que ce field (qui représente la requête à Mercanet), contienne le hash du seal
