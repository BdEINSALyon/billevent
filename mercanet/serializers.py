from rest_framework import serializers
from models import TransactionMercanet
import sealTransaction
class TransactionMercanetSerializer(serializers.Serializer):
    idTransaction = serializers.IntegerField(required = True)
    idTransaction = serializers.IntegerField(required = True)
    transactionTS = serializers.BooleanField(required = True)
    transactionState = serializers.CharField(max_length = 100)
    paymentMethod = serializers.BooleanField(required = False) # ce sera toujours en CB, non ?
    idOrder = Serializer.IntegerField(required = True)
# comment peut-on ajouter le seal à ce serializer ? il faut que ce field (qui représente la requête à Mercanet), contienne le hash du seal
