from django.contrib.auth.models import User, Group
from rest_framework import serializers

from api import models
from api.models import Event


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
        fields = ('type', 'value')


class QuestionSerializer(serializers.ModelSerializer):
    class Meta:
        read_only = True
        model = models.Question
        fields = ('question', 'help_text', 'question_type', 'required')


class OptionSerializer(serializers.ModelSerializer):
    rules = PricingRuleSerializer(many=True, read_only=True)
    questions = QuestionSerializer(many=True, read_only=True)

    class Meta:
        model = models.Option
        fields = ('name',
                  'price_ht', 'price_ttc',
                  'rules',
                  'questions', 'event')


class ProductSerializer(serializers.ModelSerializer):
    rules = PricingRuleSerializer(many=True, read_only=True)
    options = OptionSerializer(many=True, read_only=True)
    questions = QuestionSerializer(many=True, read_only=True)

    class Meta:
        model = models.Product
        fields = ('name',
                  'price_ht', 'price_ttc',
                  'rules', 'options',
                  'questions', 'event')


class EventSerializer(serializers.ModelSerializer):
    products = ProductSerializer(many=True, read_only=True)

    class Meta:
        model = models.Event
        fields = ('name', 'description',
                  'sales_opening', 'sales_closing',
                  'logo_url', 'products')
        depth = 10


class OrderSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.Order
        fields = ('id', 'client', 'event', 'billets')
        depth = 10
