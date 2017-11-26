from rest_framework import serializers
from mercanet.models import TransactionMercanet
class TransactionMercanetSerializer(serializers.ModelSerializer):#pour le 1er enregistrement, avant paiement
   class Meta:
       model = TransactionMercanet
       fields= '__all__'