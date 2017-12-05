from django.core.signing import TimestampSigner
from django.shortcuts import render
from django.http import HttpResponseNotFound, Http404
from api.models import Order
from ticketgenerator import generator


def generate_ticket(request, id):
    real_id = TimestampSigner().unsign(id)
    try:
        order = Order.objects.get(id=real_id)
    except Order.DoesNotExist:
        raise Http404("Does not exist")
    if order.status != Order.STATUS_VALIDATED:
        raise Http404("Does not exist")
    response = generator.generate(order)
    return response
