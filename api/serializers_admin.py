from django.contrib.auth.models import User, Group
from rest_framework import serializers
from rest_framework.relations import PrimaryKeyRelatedField

from api import models
from api.models import Billet, Product, Option


class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = ('url', 'username', 'email', 'groups')


class PricingRuleSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.PricingRule
        fields = ('id', 'type', 'value')


class QuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Question
        fields = ('id', 'question', 'help_text', 'data', 'question_type', 'required', 'target')


class AnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Answer
        fields = ('id', 'participant', 'question', 'value', 'order', 'billet')


class OptionSerializer(serializers.ModelSerializer):
    rules = PricingRuleSerializer(many=True)

    class Meta:
        model = models.Option
        fields = ('id', 'name', 'type',
                  'price_ht', 'price_ttc',
                  'rules', 'seats', 'target',
                  'event')


class ParticipantSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Participant
        fields = ('id', 'first_name', 'last_name', 'phone', 'email', 'billet')


class ProductSerializer(serializers.ModelSerializer):
    rules = PricingRuleSerializer(many=True)
    options = OptionSerializer(many=True, read_only=True)
    questions = QuestionSerializer(many=True)

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


class ClientSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Client
        fields = ('id', 'first_name', 'last_name', 'email', 'phone')


class InvitationSerializer(serializers.ModelSerializer):
    event = EventSerializer(read_only=True)
    event_id = serializers.PrimaryKeyRelatedField(
        queryset=models.Event.objects.all(), source='event', write_only=True)

    class Meta:
        model = models.Invitation
        fields = ('id', 'first_name', 'last_name', 'email', 'event', 'event_id', 'token', 'seats', 'bought_seats')
        depth = 3

    def create(self, validated_data):
        invitation, created = models.Invitation.objects.get_or_create(email=validated_data['email'],
                                                                      event=validated_data['event'],
                                                                      defaults=validated_data)
        if not created:
            self.update(invitation, validated_data)
        return invitation


class BilletOptionSerializer(serializers.ModelSerializer):
    option = OptionSerializer()

    class Meta:
        model = models.BilletOption
        fields = ('id', 'option', 'participant', 'amount', 'billet')


class BilletOptionInputSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.BilletOption
        fields = ('id', 'option', 'participant', 'amount', 'billet')


class SimpleOrderSerializer(serializers.ModelSerializer):
    answers = AnswerSerializer(many=True)
    client = ClientSerializer(read_only=True)

    class Meta:
        model = models.Order
        fields = ('id', 'client', 'status', 'answers')
        depth = 2


class BilletSerializer(serializers.ModelSerializer):
    product = ProductSerializer(many=False)
    participants = ParticipantSerializer(many=True)
    billet_options = BilletOptionSerializer(many=True)
    order = SimpleOrderSerializer(read_only=True)

    class Meta:
        model = models.Billet
        fields = ('id', 'product', 'billet_options', 'participants', 'order')
        depth = 2


class OrderSerializer(serializers.ModelSerializer):
    event = EventSerializer(read_only=True)
    billets = BilletSerializer(many=True)
    answers = AnswerSerializer(many=True)
    client = ClientSerializer(read_only=True)

    class Meta:
        model = models.Order
        fields = ('id', 'client', 'event', 'billets', 'status', 'amount', 'answers')
        depth = 2


class CategorieSerializer(serializers.ModelSerializer):
    products = ProductSerializer(many=True)

    class Meta:
        model = models.Categorie
        fields = ('name', 'desc', 'products')
