from django.shortcuts import render

# Create your views here.
from reportlab.lib.pagesizes import A4, landscape
from reportlab.pdfgen import canvas
from django.http import HttpResponse
from reportlab.lib.units import mm


def generate_ticket(request):
    holder_last_name = "SKYWALKER"
    holder_first_name = "Anakin"
    buyer_last_name = "SKYWALKER"
    buyer_first_name = "Luke"
    statut = "Payé"
    prix = 42
    jour = 4
    mois = 2
    année = 8666
    date = "{}/{}/{}".format(jour, mois, année)
    # Create the HttpResponse object with the appropriate PDF headers.
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="ticket.pdf"'

    # Create the PDF object, using the response object as its "file."
    p = canvas.Canvas(response, pagesize=landscape(A4))

    # Draw things on the PDF. Here's where the PDF generation happens.
    # See the ReportLab documentation for the full list of functionality.
    p.rect(20*mm, A4[0]-(20+45.70)*mm, 62.70*mm, 45.70*mm, stroke=1, fill=0)
    p.drawString((20+62.70*0.1)*mm, A4[0]-(20+45.70*0.5)*mm, "Je suis un code barre !")
    p.drawString(20 * mm, A4[0] - (20 + 45.70 + 10) * mm, "{}".format(last_name))
    p.drawString(20 * mm, A4[0] - (20 + 45.70 + 20) * mm, "{}".format(first_name))
    p.drawString(20 * mm, A4[0] - (20 + 45.70 + 30) * mm, "Statut : {}".format(statut))
    p.drawString(20 * mm, A4[0] - (20 + 45.70 + 40) * mm, "Prix TTC : {} €".format(prix))
    p.drawString(20 * mm, A4[0] - (20 + 45.70 + 50) * mm, "Date d'émission : {}".format(date))
    p.drawImage("ticketgenerator/bde.png", A4[1]-(20+22.53)*mm,A4[0]-(20+30)*mm, width=22.53*mm,height=30*mm,mask=None)
    p.drawString(90*mm, 20*mm, "Billet vendu et édité par le BdE INSA Lyon, 20 avenue Albert Einstein, 69621 Villeurbanne CEDEX")

    # Close the PDF object cleanly.
    p.showPage()
    p.save()

    return response
