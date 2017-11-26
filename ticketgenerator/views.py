from django.core.signing import TimestampSigner
from django.shortcuts import render
from api.models import Billet, Event, Order
from ticketgenerator import generator


def generate_ticket(request, id):
    real_id = TimestampSigner().unsign(id)
    order = Order.objects.get(id=real_id, status=Order.STATUS_VALIDATED)
    response = generator.generate(order)
    return response
