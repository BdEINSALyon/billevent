from audioop import bias

from django.contrib.auth.models import User, Group
from django.http import HttpResponseNotFound
# from httplib2 import Response
from rest_framework import viewsets, status
from rest_framework.decorators import detail_route, api_view
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
import datetime

from api import permissions
from api.models import Event, Order, Option, Product, Billet, PricingRule, Question, Participant, Categorie
from api.serializers import BilletSerializer, CategorieSerializer
from .serializers import UserSerializer, GroupSerializer, EventSerializer, OrderSerializer, OptionSerializer, \
    ProductSerializer

plus_disponible_view = Response("Ce que vous demandez n'est plus disponible",status=status.HTTP_200_OK)
invalid_request_view = Response("Requête invalide, les paramètres spécifiés dans le POST sont non conformes",status=status.HTTP_400_BAD_REQUEST)

class EventsViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Event.objects.all()
    serializer_class = EventSerializer

    # permission_classes = permissions.IsAuthenticatedAndReadOnly

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


"""
class OptionViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Option.objects.all()
    serializer_class = OptionSerializer

"""


class ProductViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Le viewset pour les produits:

    Faire le requête avec le paramètre GET \'event\' permet de filtrer la requête par event.
    """

    serializer_class = ProductSerializer

    # permission_classes = permissions.IsAuthenticatedAndReadOnly

    def get_queryset(self):
        event_id = self.request.GET.get("event")
        print(event_id)
        if event_id is None:
            return Product.objects.all()

        return Product.objects.filter(event=event_id)


class OptionViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Le viewset pour les option:

    Faire le requête avec le paramètre GET \'produit\' permet de filtrer la requête par produit.
    """

    serializer_class = OptionSerializer
    permission_classes = permissions.IsAuthenticatedAndReadOnly

    def get_queryset(self):
        produit_id = self.request.GET.get("produit")
        if produit_id is None:
            return Option.objects.all()

        return Option.objects.filter(products=produit_id)


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
        if Product.objects.get(id=request.data['product']).how_many_left > 0:
            #On crée un sérializer contenant les data envoyés par l'utilisateur pour checker si ce qui est envoyé est bien un billet
            billet = BilletSerializer(data=request.data)
            if billet.is_valid():   #Si le billet est valide




                new_billet = Billet(id=Billet.objects.count()+1, product=Product.objects.get(id=billet.data['product']),
                                    options=Option.objects.filter(id=billet.data['options'][0]))

                new_billet.save()

                return Response(billet.data, status=status.HTTP_201_CREATED)
            return Response(billet.errors, status=status.HTTP_400_BAD_REQUEST)
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

            ancien_billet = Billet.objects.get(billet.data.id)

            for option in billet.data['options']:
                if Option.objects.get(option.id):
                    return plus_disponible_view
            if Option.objects.get(id=billet.data):
                ancien_billet.options = billet.data['options']
                ancien_billet.save()
                return BilletSerializer(ancien_billet)
        return invalid_request_view


