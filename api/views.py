from django.contrib.auth.models import User, Group
from rest_framework import viewsets, status
from rest_framework.decorators import detail_route, api_view
from rest_framework.response import Response

from api.models import Event, Order, Option, Product
from .serializers import UserSerializer, GroupSerializer, EventSerializer, OrderSerializer, OptionSerializer


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



@api_view(['GET'])
def products_list(request, event):
    """

    :param request:
    :param event: L'évenement dont on veut les produits
    :return: 404 or liste des produits
    """
    try:
        products = Product.objects.filter(event=event);
    except Product.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == "GET":
        return Response(OptionSerializer(products,many="true").data)

