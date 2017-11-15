from django.contrib.auth.models import User, Group
from django.http import HttpResponseNotFound
# from httplib2 import Response
from rest_framework import viewsets, status
from rest_framework.decorators import detail_route, api_view
from rest_framework.response import Response
from rest_framework.views import APIView

from api.models import Event, Order, Option, Product, Billet, PricingRule, Question
from .serializers import UserSerializer, GroupSerializer, EventSerializer, OrderSerializer, OptionSerializer, \
    ProductSerializer


class EventsViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Event.objects.all()
    serializer_class = EventSerializer

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

    def get_queryset(self):
        produit_id = self.request.GET.get("produit")
        if produit_id is None:
            return Option.objects.all()

        return Option.objects.filter(products=produit_id)
