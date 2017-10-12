from rest_framework import serializers
from models import TransactionMercanet
class TransactionMercanetSerializer(serializers.Serializer):
    amount = serializers.IntegerField(required = True)
    currencyCode = serializers.IntegerField(require = True)
    interfaceVersion = serializers.CharField(min_length = 1)
    keyVersion = serializers.IntegerField()
    merchantId = serializers.CharField()
    normalReturnUrl = serializers.URLField()
    orderChannel = serializers.CharField()
    transactionReference = serializers.IntegerField()
    Seal = serializers.CharField(min_length = 1)

# comment peut-on ajouter le seal à ce serializer ? il faut que ce field (qui représente la requête à Mercanet), contienne le hash du seal
