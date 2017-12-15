from django.contrib.auth.models import User, Group
from rest_framework import serializers
from rest_framework.relations import PrimaryKeyRelatedField

from api import models
from api.models import Billet, Product, Option


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('username', 'email')


class GroupSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Group
        fields = ('url', 'name')


class PricingRuleSerializer(serializers.ModelSerializer):
    class Meta:
        read_only = True
        model = models.PricingRule
        fields = ('id', 'type', 'value')


class CouponSerializer(serializers.ModelSerializer):
    class Meta:
        read_only = True
        model = models.Coupon
        fields = ('id', 'percentage', 'amount', 'description')


class QuestionSerializer(serializers.ModelSerializer):
    class Meta:
        read_only = True
        model = models.Question
        fields = ('id', 'question', 'help_text', 'data', 'question_type', 'required', 'target')


class AnswerSerializer(serializers.ModelSerializer):
    class Meta:
        read_only = True
        model = models.Answer
        fields = ('id', 'participant', 'question', 'value', 'order', 'billet')


class OptionSerializer(serializers.ModelSerializer):
    rules = PricingRuleSerializer(many=True, read_only=True)

    class Meta:
        model = models.Option
        fields = ('id', 'name', 'type', 'description',
                  'price_ht', 'price_ttc',
                  'rules', 'seats', 'target',
                  'event', 'how_many_left')


class ParticipantSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Participant
        fields = ('id', 'first_name', 'last_name', 'phone', 'email', 'billet')


class ProductSerializer(serializers.ModelSerializer):
    rules = PricingRuleSerializer(many=True, read_only=True)
    options = OptionSerializer(many=True, read_only=True)
    questions = QuestionSerializer(many=True, read_only=True)

    class Meta:
        model = models.Product
        fields = ('id', 'name',
                  'price_ht', 'price_ttc',
                  'rules', 'options', 'seats', 'description',
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
    client = ClientSerializer(read_only=True)

    class Meta:
        model = models.Invitation
        fields = ('id', 'client', 'event', 'token', 'bought_seats', 'seats')
        depth = 3


class BilletOptionSerializer(serializers.ModelSerializer):
    option = OptionSerializer()

    class Meta:
        model = models.BilletOption
        fields = ('id', 'option', 'participant', 'amount', 'billet')


class BilletOptionInputSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.BilletOption
        fields = ('id', 'option', 'participant', 'amount', 'billet')


class BilletSerializer(serializers.ModelSerializer):
    product = PrimaryKeyRelatedField(many=False, queryset=Product.objects.all())
    options = PrimaryKeyRelatedField(many=True, read_only=True, required=False)
    participants = ParticipantSerializer(many=True, required=False)
    billet_options = BilletOptionSerializer(many=True, required=False)

    class Meta:
        model = models.Billet
        fields = ('id', 'product', 'options', 'billet_options', 'participants')
        depth = 2


class BilletForOrderSerializer(serializers.ModelSerializer):
    product = ProductSerializer(many=False)
    billet_options = BilletOptionSerializer(many=True, required=False)
    options = PrimaryKeyRelatedField(many=True, read_only=True, required=False)
    participants = ParticipantSerializer(many=True, required=False)

    class Meta:
        model = models.Billet
        fields = ('id', 'product', 'options', 'billet_options', 'participants')
        depth = 2


class OrderSerializer(serializers.ModelSerializer):
    event = EventSerializer(read_only=True)
    billets = BilletForOrderSerializer(many=True, read_only=True)
    answers = AnswerSerializer(many=True, read_only=True)
    client = ClientSerializer(read_only=True)
    coupon = CouponSerializer(read_only=True)

    class Meta:
        model = models.Order
        fields = ('id', 'client', 'event', 'billets', 'status', 'answers', 'coupon')
        depth = 2


class CategorieSerializer(serializers.ModelSerializer):
    products = ProductSerializer(many=True)

    class Meta:
        model = models.Categorie
        fields = ('name', 'desc', 'products')
