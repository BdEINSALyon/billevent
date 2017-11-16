from django.contrib.auth.models import User, Group
from rest_framework import serializers

from api import models


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
        fields = ('id', 'question', 'help_text', 'question_type', 'required')


class OptionSerializer(serializers.ModelSerializer):
    rules = PricingRuleSerializer(many=True, read_only=True)
    questions = QuestionSerializer(many=True, read_only=True)

    class Meta:
        model = models.Option
        fields = ('id', 'name',
                  'price_ht', 'price_ttc',
                  'rules',
                  'questions', 'event')


class ProductSerializer(serializers.ModelSerializer):
    rules = PricingRuleSerializer(many=True, read_only=True)
    options = OptionSerializer(many=True, read_only=True)
    questions = QuestionSerializer(many=True, read_only=True)

    class Meta:
        model = models.Product
        fields = ('id', 'name',
                  'price_ht', 'price_ttc',
                  'rules', 'options',
                  'questions', 'event', 'can_buy_one_more')


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
        fields = ('id', 'client', 'event', 'billets')
        depth = 10


class BilletSerializer(serializers.ModelSerializer):

    product = ProductSerializer(read_only=True)
    options = OptionSerializer(read_only=True, many=True)

    class Meta:
        model = models.Billet
        fields = ('id', 'product', 'options')

