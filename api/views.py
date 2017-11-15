from django.contrib.auth.models import User, Group
from rest_framework import viewsets, status
from rest_framework.decorators import detail_route, api_view
from rest_framework.response import Response

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



@api_view(['GET'])
def products_by_id(request, id):
    """

    :param request:
    :param id: L'ID du produit que l'on souhaite avoir
    :return: 404 ou le produit demandé
    """
    try:
        product = Product.objects.filter(id=id);
    except Product.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == "GET":
        return Response(ProductSerializer(product).data)

@api_view(['GET'])
def option_by_id(request, id):
    """

    :param request:
    :param id: L'ID du produit que l'on souhaite avoir
    :return: 404 ou le produit demandé
    """
    try:
        product = Option.objects.filter(id=id);
    except Option.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == "GET":
        return Response(OptionSerializer(product).data)


@api_view(['GET'])
def option_by_product(request, product_id):
    """

    :param request:
    :param product_id: L'id du produit auquel sont reliées les options
    :return: 404 ou la liste des produits
    """

    try:
        options = Option.objects.filter(products=product_id)
    except Option.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == "GET":
        return Response(OptionSerializer(options,many="true").data)

@api_view(['GET'])
def canBuyOneMoreProduct(request, product_id):
    """
    Allow the user to know if there are still availables billets

    :param request:
    :param id: The id of the product
    :return: True si il reste des places, ou si il n'existe pas de quotas, false si il n'y a pas de places ou si le programme renvoie une erreur
    """


    try:
        BilletsMax = Product.objects.get(id=product_id).rules.get(type="T").value
        nombreBillet = Billet.objects.filter(product=product_id).count()

    except Product.DoesNotExist:
        return Response(False)
    except Billet.DoesNotExist:
        return Response(True)
    if BilletsMax-nombreBillet>0:
        return True
    else:
        return False
@api_view(['GET'])
def canBuyOneMoreOption(request, option_id):
    """
    Allow the user to know if there are still availables billets

    :param request:
    :param id: The id of the product
    :return: True si il reste des places, ou si il n'existe pas de quotas, false si il n'y a pas de places ou si le programme renvoie une erreur
    """


    try:
        BilletsMax = Option.objects.get(id=option_id).rules.get(type="T").value
        nombreBillet = Billet.objects.filter(option=option_id).count()

    except Product.DoesNotExist:
        return Response(False)
    except Billet.DoesNotExist:
        return Response(True)
    if BilletsMax-nombreBillet>0:
        return True
    else:
        return False

@api_view(['GET'])
def question_by_Product(request,id_product):
    """
    Permet de récupérer les question liées aux produits

    :param request:
    :param id_product: Le produit
    :return: La liste JSON des questions liées
    """

    return Response(Question.objects.filter(product=id_product).data)