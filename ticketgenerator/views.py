from django.shortcuts import render

# Create your views here.
from reportlab.lib.pagesizes import A4, landscape
from reportlab.pdfgen import canvas
from django.http import HttpResponse
from reportlab.lib.units import mm


def generate_ticket(request):
    uid = "MAO0RTFM"
    order = "NEOMATRIX"
    holder_last_name = "SKYWALKER"
    holder_first_name = "Anakin"
    buyer_last_name = "SKYWALKER"
    buyer_first_name = "Luke"
    status = "Payé"
    price = 42
    issuing_day = 6
    issuing_month = 6
    issuing_year = 6666
    issuing_date = "{}/{}/{}".format(issuing_day, issuing_month, issuing_year)
    order_day = 4
    order_month = 2
    order_year = 4242
    order_date = "{}/{}/{}".format(order_day, order_month, order_year)
    # Create the HttpResponse object with the appropriate PDF headers.
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="ticket.pdf"'

    # Create the PDF object, using the response object as its "file."
    p = canvas.Canvas(response, pagesize=landscape(A4))

    # Draw things on the PDF. Here's where the PDF generation happens.
    # See the ReportLab documentation for the full list of functionality.
    p.rect(20 * mm, A4[0] - (20 + 45.70) * mm, 62.70 * mm, 45.70 * mm, stroke=1, fill=0)
    p.drawString((20 + 62.70 * 0.1) * mm, A4[0] - (20 + 45.70 * 0.5) * mm, "Je suis un code barre !")
    p.drawString(20 * mm, A4[0] - (20 + 45.70 + 10) * mm, "{}".format(holder_last_name))
    p.drawString(20 * mm, A4[0] - (20 + 45.70 + 20) * mm, "{}".format(holder_first_name))
    p.drawString(20 * mm, A4[0] - (20 + 45.70 + 30) * mm, "Statut : {}".format(status))
    p.drawString(20 * mm, A4[0] - (20 + 45.70 + 40) * mm, "Prix TTC : {} €".format(price))
    p.drawString(20 * mm, A4[0] - (20 + 45.70 + 50) * mm, "Date d'émission : {}".format(issuing_date))
    p.drawString(70 * mm, A4[0] - (20 + 45.70 + 10) * mm, "Numéro : {}".format(uid))
    p.drawString(70 * mm, A4[0] - (20 + 45.70 + 20) * mm, "Organisateur : BdE INSA Lyon")
    p.drawString(70 * mm, A4[0] - (20 + 45.70 + 30) * mm, "Acheteur : {} {}".format(buyer_last_name, buyer_first_name))
    p.drawString(70 * mm, A4[0] - (20 + 45.70 + 40) * mm, "Date de commande : {}".format(order_date))
    p.drawString(70 * mm, A4[0] - (20 + 45.70 + 50) * mm, "Numéro de commande : {}".format(order))
    p.drawString(70 * mm, A4[0] - (20 + 45.70 + 60) * mm, "Valable pour : 1 personne")
    p.drawImage("ticketgenerator/bde.png", A4[1] - (20 + 22.53) * mm, A4[0] - (20 + 30) * mm, width=22.53 * mm,
                height=30 * mm, mask=None)
    p.drawString(90 * mm, 20 * mm,
                 "Billet vendu et édité par le BdE INSA Lyon, 20 avenue Albert Einstein, 69621 Villeurbanne CEDEX")

    # Close the PDF object cleanly.
    p.showPage()
    p.save()

    return response
