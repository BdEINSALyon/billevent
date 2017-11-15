from rest_framework import serializers
from models import TransactionMercanet
class TransactionMercanetSerializer(serializers.Serializer):
    class Meta:
        model = TransactionMercanet
        fields = ('amount', 'currencyCode', 'interfaceVersion', 'keyVersion', 'merchantID', 'normalReturnUrl', 'transactionReference', 'Seal')

# comment peut-on ajouter le seal à ce serializer ? il faut que ce field (qui représente la requête à Mercanet), contienne le hash du seal
