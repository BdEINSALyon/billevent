from django.contrib.auth.models import User, Group
from rest_framework import serializers
from rest_framework.relations import PrimaryKeyRelatedField

from api import models
from api.models import Billet, Product, Option


class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = ('url', 'username', 'email', 'groups')


class GroupSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Group
        fields = ('url', 'name')


class PricingRuleSerializer(serializers.ModelSerializer):
    class Meta:
        read_only = True
        model = models.PricingRule
        fields = ('id', 'type', 'value')


class QuestionSerializer(serializers.ModelSerializer):
    class Meta:
        read_only = True
        model = models.Question
        fields = ('id', 'question', 'help_text', 'question_type', 'required', 'target')


class OptionSerializer(serializers.ModelSerializer):
    rules = PricingRuleSerializer(many=True, read_only=True)

    class Meta:
        model = models.Option
        fields = ('id', 'name',
                  'price_ht', 'price_ttc',
                  'rules', 'seats', 'target',
                  'event', 'how_many_left')


class ParticipantSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Participant
        fields = "__all__"


class ProductSerializer(serializers.ModelSerializer):
    rules = PricingRuleSerializer(many=True, read_only=True)
    options = OptionSerializer(many=True, read_only=True)
    questions = QuestionSerializer(many=True, read_only=True)

    class Meta:
        model = models.Product
        fields = ('id', 'name',
                  'price_ht', 'price_ttc',
                  'rules', 'options', 'seats',
                  'questions', 'event', 'how_many_left', 'categorie')


class OrganizerSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Organizer
        fields = ('id', 'name', 'phone', 'address', 'email')


class EventSerializer(serializers.ModelSerializer):
    organizer = OrganizerSerializer()

    class Meta:
        model = models.Event
        fields = ('id', 'name', 'description',
                  'sales_opening', 'sales_closing',
                  'start_time', 'end_time',
                  'website', 'place', 'address', 'organizer',
                  'logo_url')
        depth = 10


class OrderSerializer(serializers.ModelSerializer):
    event = EventSerializer(read_only=True)

    class Meta:
        model = models.Order
        fields = ('id', 'client', 'event')
        depth = 0


class ClientSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Client
        fields = ('id', 'first_name', 'last_name', 'email', 'phone')


class InvitationSerializer(serializers.ModelSerializer):
    event = EventSerializer(read_only=True)
    client = ClientSerializer(read_only=True)

    class Meta:
        model = models.Invitation
        fields = ('id', 'client', 'event', 'token')
        depth = 3


class BilletSerializer(serializers.ModelSerializer):
    product = PrimaryKeyRelatedField(many=False, queryset=Product.objects.all())
    options = PrimaryKeyRelatedField(many=True, required=False, queryset=Option.objects.all())

    class Meta:
        model = models.Billet
        fields = ('id', 'product', 'options')
        depth = 1


class CategorieSerializer(serializers.ModelSerializer):
    products = ProductSerializer(many=True)

    class Meta:
        model = models.Categorie
        fields = ('name', 'desc', 'products')
