from datetime import datetime

from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils.decorators import method_decorator
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
from api.models import Event, Order, Option, Product, Billet, Categorie, Invitation, Client, BilletOption
from api.serializers import BilletSerializer, CategorieSerializer, InvitationSerializer
from .serializers import EventSerializer, OrderSerializer, OptionSerializer, \
    ProductSerializer

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
    def order(self, request, pk=None):
        event = self.get_object()
        order_id = 'order_' + event.id.__str__()
        if order_id in request.session:
            order = Order.objects.get(id=request.session[order_id])
        else:
            order = Order(event=event)
            order.save()
            request.session[order_id] = order.id
        return Response(OrderSerializer(order).data)

    @detail_route(methods=['get'])
    def categorie(self, request, pk=None):
        event = self.get_object()
        return Response(CategorieSerializer(Categorie.objects.filter(event=event).all(), many=True).data)

    @detail_route(methods=['post'])
    def order(self, request, pk=None):

        event = Event.for_user(request.user).get(id=pk)
        client = request.user.client

        order = client.orders.filter(event=event, status__lt=Order.STATUS_VALIDATED).first() or \
                Order(event=event, client=client)
        order.save()

        transaction.atomic()

        if "billets" in request.data:
            for billet in request.data['billets']:
                # Si le billet est update
                if "id" not in billet:
                    billet_data = BilletSerializer(data=billet, context={"order": order.id})
                    if billet_data.is_valid():
                        billet = billet_data.create()
                        billet.save()

        # On dit que la commande est liée à un événement
        return Response(OrderSerializer(order).data)


"""
class OptionViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Option.objects.all()
    serializer_class = OptionSerializer

"""


class OrderViewSet(viewsets.ModelViewSet):
    serializer_class = OrderSerializer

    def get_queryset(self):
        event_id = self.request.GET.get("event")
        if event_id is None:
            raise APIException('No event id given', 400)

        return Order.objects.filter(client__user=self.request.user)


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
