from datetime import datetime, timedelta

from django.core.exceptions import ValidationError
from django.core.signing import TimestampSigner
from django.db import transaction
from django.utils.decorators import method_decorator
from django.utils import timezone
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from rest_framework import viewsets, status
from rest_framework.decorators import detail_route, authentication_classes, permission_classes
from rest_framework.exceptions import APIException
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_jwt.settings import api_settings

from api import permissions
from api.models import Event, Order, Option, Product, Billet, Categorie, Invitation, Client, BilletOption, Coupon
from api.serializers import BilletSerializer, CategorieSerializer, InvitationSerializer, ParticipantSerializer, \
    AnswerSerializer, BilletOptionSerializer, BilletOptionInputSerializer, UserSerializer
from mercanet.models import TransactionRequest
from .serializers import EventSerializer, OrderSerializer, OptionSerializer, \
    ProductSerializer
from django import urls

plus_disponible_view = Response("Ce que vous demandez n'est plus disponible", status=status.HTTP_200_OK)
invalid_request_view = Response("Requête invalide, les paramètres spécifiés dans le POST sont non conformes",
                                status=status.HTTP_400_BAD_REQUEST)


class EventsViewSet(viewsets.ModelViewSet):
    queryset = Event.objects.all()
    serializer_class = EventSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Event.for_user(self.request.user)

    @detail_route(methods=['get'])
    def categorie(self, request, pk=None):
        """Permet de récupérer toutes les catégories liées à l'évenement
        """
        event = self.get_object()
        return Response(CategorieSerializer(Categorie.objects.filter(event=event).all(), many=True).data)

    @detail_route(methods=['get'])
    def invitation(self, request, pk):
        return Response(InvitationSerializer(request.user.client.invitations.get(event_id=pk)).data)

    @detail_route(methods=['get', 'post'])
    def order(self, request, pk=None):
        """Permet de créer une commande.

         Il faut envoyer un dictionaire dont la valeur "billets" correspondt à un tableau contenat les billest
        """

        # On récupère l'évenement en s'assurant au passage que l'utilisateur a le droit  d'y accéder
        event = Event.for_user(request.user).get(id=pk)
        # On récupère le client lié à l'user
        client = request.user.client

        # On récupère la commande en cours si il en existe une, sinon on la crée
        order = client.orders.filter(event=event, status__lt=Order.STATUS_PAYMENT,
                                     created_at__gt=timezone.now() - timedelta(minutes=20)).first() or \
                Order(event=event, client=client, status=Order.STATUS_SELECT_PRODUCT)
        order.save()

        if request.method == 'GET':
            return Response(OrderSerializer(order).data)

        # On place le status en sélection de produit
        order.status = order.STATUS_SELECT_PRODUCT
        order.save()

        order.billets.all().delete()

        # Si il y a un champ billets dans les données renvoyées
        if "billets" in request.data:
            # Pour chaque billet dans l'array de billets
            for billet in request.data['billets']:
                # Si le billet est update
                if "id" not in billet:
                    billet_data = BilletSerializer(data=billet, context={"order": order.id})
                    if billet_data.is_valid():
                        billet_data.validated_data['order'] = order
                        billet = billet_data.create(billet_data.validated_data)
                        billet.save()

        ok = order.is_valid()
        # Si la commande ne répond pas aux règles
        if not ok:
            order.destroy_all()
            return Response("NIQUE TA MERE ESSAYE PAS DE GRUGER", status=400)

        order.status = order.STATUS_SELECT_PARTICIPANT
        order.save()

        return Response(OrderSerializer(order).data)

    @detail_route(methods=['post'])
    def options(self, request, pk=None, *args, **kwargs):

        event = Event.for_user(request.user).get(id=pk)
        client = request.user.client
        order = client.orders.get(event=event, status__lt=Order.STATUS_PAYMENT)
        transaction.atomic()

        for optionbillet in request.data:
            if "billet" in optionbillet and optionbillet['billet'].isDigit():
                # Récupère le billet et renvoie une erreur si le billet n'est pas dans la commande
                billet = order.billets.get(id=int(optionbillet['billet']))
            else:
                billet = order.option_billet

            # Récupère l'option et renvoie une erreur si l' option n'est pas liée au produit du billet
            option = billet.product.options.get(id=int(optionbillet['option']))
            participant = None

            if "participant" in optionbillet and optionbillet['participant'].isdigit():
                participant = billet.participants.get(id=int(optionbillet['participant']))

            BilletOption(billet=billet, option=option, amount=int(optionbillet['amount']),
                         participant=participant).save()

        if not order.is_valid():
            transaction.rollback()
            return Response("NIQUE TA MERE ESSAYE PAS DE GRUGER")

        order.status = order.STATUS_PAYMENT
        order.save()

        return Response(OrderSerializer(order).data)


"""
class OptionViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Option.objects.all()
    serializer_class = OptionSerializer
"""


class OrderViewSet(viewsets.ModelViewSet):
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Order.objects.filter(client__user=self.request.user)

    @detail_route(methods=['post'])
    def coupon(self, request, **kwargs):
        order = self.get_object()
        req_code = request.data['code']
        if not req_code or req_code == '':
            order.coupon = None
            order.save()
            return Response(OrderSerializer(order).data)
        code = Coupon.objects.get(code=request.data['code'], event=order.event)
        if order.can_use_coupon(code):
            order.coupon = code
            order.save()
            return Response(OrderSerializer(order).data)
        return Response(status=404)

    @detail_route(methods=['post'])
    def participants(self, request, pk):
        order = self.get_object()

        # Pour chaque participant dans le JSON
        for participant_data in request.data:
            # On crée le sérializer et on regarde si il est valide, comme d'hab
            participant_ser = ParticipantSerializer(data=participant_data)
            if participant_ser.is_valid():
                participant = participant_ser.create(participant_ser.validated_data)
                if participant.billet.product.seats >= participant.billet.participants.count():
                    participant.save()
                else:
                    participant.delete()
            else:
                return Response(participant_ser.errors)

        order.state = Order.STATUS_SELECT_QUESTION
        order.save()

        return Response(OrderSerializer(self.get_object()).data)

    @detail_route(methods=['post'])
    def answers(self, request, pk):
        order = self.get_object()

        order.answers.all().delete()

        # Pour chaque participant dans le JSON
        for answer_data in request.data:
            # On crée le sérializer et on regarde si il est valide, comme d'hab
            answer_data['order'] = pk
            answer_serializer = AnswerSerializer(data=answer_data)
            if answer_serializer.is_valid():
                answer = answer_serializer.create(answer_serializer.validated_data)
                answer.save()
            else:
                return Response(answer_serializer.errors)

        order.status = Order.STATUS_SELECT_OPTIONS
        order.save()

        return Response(OrderSerializer(order).data)

    @detail_route(methods=['post'])
    def billet_options(self, request, pk):
        order = self.get_object()

        for billet in order.billets.all():
            billet.billet_options.all().delete()

        # Pour chaque participant dans le JSON
        for bo_data in request.data:
            # On crée le sérializer et on regarde si il est valide, comme d'hab
            bo_data['order'] = pk
            if 'billet' not in bo_data or bo_data['billet'] is None:
                billet, _ = order.billets.get_or_create(product=None)
                bo_data['billet'] = billet.id
            bo_serializer = BilletOptionInputSerializer(data=bo_data)
            if bo_serializer.is_valid():
                bo = bo_serializer.create(bo_serializer.validated_data)
                bo.save()
            else:
                return Response(bo_serializer.errors)

        if order.is_valid():
            order.status = Order.STATUS_REVIEW_ORDER
            order.save()
            return Response(OrderSerializer(order).data)
        else:
            for billet in order.billets.all():
                billet.billet_options.all().delete()

            return Response({"error": "Les options dépassent les quotas"}, status=400)

    @detail_route(methods=['post'])
    def cancel(self, request, pk):
        order = self.get_object()
        order.status = Order.STATUS_CANCELED
        order.save()
        if order.delete():
            return Response({'success': True})
        else:
            return Response({'success': False})

    @detail_route(methods=['get'])
    def final(self, request, pk):
        id = pk
        order = Order.objects.get(id=id, client__user=request.user)

        status = "waiting"
        if order.status == Order.STATUS_VALIDATED:
            status = "validated"
        elif order.status >= Order.STATUS_REJECTED:
            status = "rejected"

        tickets = request.build_absolute_uri(
            urls.reverse('ticket-print', args=[TimestampSigner().sign(id)]))

        return Response({
            'status': status,
            'url': tickets
        })

    @detail_route(methods=['post'])
    def pay(self, request, pk=None):
        """Renvoie l'url vers la page de paiement, prend en paramètre post "callback" une adresse (JSP LAQUELLE C)"""
        # On récupère la commande
        order = self.get_queryset().get(id=pk)
        # On récupère l'url de callback pour mercanet (Je sais pas ce que c'est mais c'est le front qui me l'envoie)
        callback = request.data['callback']

        amount = order.amount

        if amount > 0:
            # On crée une requête de transaction
            transaction_request = TransactionRequest(callback=callback, amount=amount * 100)
            transaction_request.save()

            # On change le statut de la commande à payé
            order.status = order.STATUS_PAYMENT
            order.transaction = transaction_request
            order.save()

            # On renvoie l'url de paiement
            return Response(request.build_absolute_uri(
                urls.reverse('mercanet-pay', args=[transaction_request.id, transaction_request.token])))
        else:
            order.status = order.STATUS_VALIDATED
            order.save()
            return Response(status=201)


class ProductViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Le viewset pour les produits:

    Faire le requête avec le paramètre GET \'event\' permet de filtrer la requête par event.
    """

    serializer_class = ProductSerializer

    # permission_classes = permissions.IsAuthenticatedAndReadOnly

    def get_queryset(self):
        events = Event.for_user(self.request.user)

        event_id = self.request.GET.get("event")
        if event_id is None:
            return Product.objects.filter(event=events)

        return Product.objects.filter(event=events.filter(id=event_id))


class OptionViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Le viewset pour les option:

    Faire le requête avec le paramètre GET \'produit\' permet de filtrer la requête par produit.
    """

    serializer_class = OptionSerializer
    permission_classes = (permissions.IsAuthenticatedAndReadOnly,)

    def get_queryset(self):
        events = Event.for_user(self.request.user)

        event_id = self.request.GET.get("event")
        if event_id is None:
            return Option.objects.filter(event=events)

        return Option.objects.filter(event=events.get(event_id))


class BilletViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = BilletSerializer
    queryset = Billet.objects.all()

    def retrieve(self, request, pk=None, *args, **kwargs):
        return Response(BilletSerializer(self.queryset.filter(id=pk).get()).data)

    def create(self, request, *args, **kwargs):
        """
        Pour créer un nouveau billet, il faut envoyer une requête POST avec l'id du produit dans le champ product et la liste des ids d'options dans le champ options

        """
        try:
            if Product.objects.get(id=request.data['product']).how_many_left > 0 or Product.objects.get(
                    id=request.data['product']).how_many_left == -1:
                # On crée un sérializer contenant les data envoyés par l'utilisateur pour checker si ce qui est envoyé est bien un billet
                billet = BilletSerializer(data=request.data)
                if billet.is_valid():  # Si le billet est valide

                    billet.validated_data['id'] = Billet.objects.count() + 1

                    new_billet = billet.create(billet.validated_data)
                    # new_billet = Billet(id=Billet.objects.count()+1, product=Product.objects.get(id=billet.data['product']),
                    #                    options=Option.objects.filter(id=billet.data['options'][0]))

                    new_billet.save()

                    return Response(BilletSerializer(new_billet).data, status=status.HTTP_201_CREATED)
                return Response(billet.errors, status=status.HTTP_400_BAD_REQUEST)
        except ValidationError as e:
            return Response(e.message)
        return Response("Plus de billets disponibles !", status=status.HTTP_200_OK)

    def update(self, request, *args, **kwargs):
        """
        Pour mettre à jour un billet, voir aussi la fonction create. Attention, met seulement à jour les options !

        :param request:
        :param args:
        :param kwargs:
        :return:
        """
        billet = BilletSerializer(data=request.data)
        if billet.is_valid():
            try:
                ancien_billet = Billet.objects.get(id=kwargs.get("pk"))
                test = billet.validated_data
                # billet.validated_data['product']=ancien_billet.product.id
                # ancien_billet.options = billet.data['options']
                test = billet.update(ancien_billet, billet.validated_data)
                ancien_billet.save()
                return Response(BilletSerializer(ancien_billet).data, status=status.HTTP_201_CREATED)
            except ValidationError as e:
                return Response(e.message)
        return invalid_request_view


@permission_classes([])
class RulesViews(APIView):
    def post(self, request):
        data = request.data
        compute = data['compute']
        data = data['data']

        if compute == 'MaxSeats':
            pricings = list(set(Product.objects.filter(id__in=data['products']))
                            .union(set(Option.objects.filter(id__in=data['options']))))
            count = 0
            for pricing in pricings:
                count += pricing.reserved_seats()
            return Response({'value': count})
        elif compute == 'InvitationsUsed':
            invitation = Invitation.objects.get(event=data['event'], client=request.user.client)
            return Response({'value': invitation.bought_seats, 'limit': invitation.seats})
        else:
            return Response(data)


@permission_classes([])
class CurrentUserViews(APIView):
    def get(self, request):
        if not request.user:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        return Response(UserSerializer(request.user).data)


@permission_classes([])
class LogoutViews(APIView):
    def delete(self, request):
        if not request.user:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        return Response(UserSerializer(request.user).data)


jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER

jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER


# noinspection PyMethodMayBeStatic
@authentication_classes([])
@permission_classes([])
class InvitationAuthentication(APIView):
    """
    Authenticate a user based on an invitation token
    """

    def post(self, request):

        if 'token' not in request.data:
            raise APIException('No token given', 400)
        token = request.data['token']
        try:
            invitation = Invitation.objects.get(token=token)
        except Invitation.DoesNotExist:
            return Response({}, status=status.HTTP_400_BAD_REQUEST)

        invitation_serializer = InvitationSerializer(invitation)

        payload = jwt_payload_handler(invitation.client.user)
        jwt_token = jwt_encode_handler(payload)

        return Response({
            'jwt': jwt_token,
            'invitation': invitation_serializer.data
        }, status=status.HTTP_202_ACCEPTED)
