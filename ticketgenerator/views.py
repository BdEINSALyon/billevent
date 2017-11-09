from django.shortcuts import render

# Create your views here.
from reportlab.lib.pagesizes import A4, landscape
from reportlab.pdfgen import canvas
from django.http import HttpResponse
from reportlab.lib.units import mm
from reportlab.graphics.shapes import Drawing
from reportlab.graphics.barcode import createBarcodeDrawing

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
    qr_x = 85.60
    qr_y = 53.98
    p.drawImage("ticketgenerator/background.png", 0 * mm, 0 * mm, width=373*mm, height=210*mm, mask=None)
    p.setFont("Helvetica", 12)
    p.setStrokeColorRGB(255,255,255)
    p.setFillColorRGB(255, 255, 255)

    p.drawString(20 * mm, A4[0] - (20 + qr_y + 10) * mm, "{}".format(holder_last_name))
    p.drawString(20 * mm, A4[0] - (20 + qr_y + 20) * mm, "{}".format(holder_first_name))
    p.drawString(20 * mm, A4[0] - (20 + qr_y + 30) * mm, "Statut : {}".format(status))
    p.drawString(20 * mm, A4[0] - (20 + qr_y + 40) * mm, "Prix TTC : {} €".format(price))
    p.drawString(20 * mm, A4[0] - (20 + qr_y + 50) * mm, "Date d'émission : {}".format(issuing_date))
    p.setFont("Helvetica-Bold", 25)
    p.drawString((20 + qr_x + 5) * mm, A4[0] - (20 + 10) * mm, "Gala INSA Lyon 2018")
    p.drawString((20 + qr_x + 5) * mm, A4[0] - (20 + 10 + 15) * mm, "9 et 10 février")
    p.drawString((20 + qr_x + 5) * mm, A4[0] - (20 + 10 + 30) * mm, "La sucrière")
    p.setFont("Helvetica", 12)
    p.drawString((20 + qr_x + 5) * mm, A4[0] - (20 + 10 + 40) * mm, "49-50 Quai Rambaud 69002 Lyon - France")
    p.drawString((20 + qr_x + 5) * mm, A4[0] - (20 + qr_y + 10) * mm, "Numéro : {}".format(uid))
    p.drawString((20 + qr_x + 5) * mm, A4[0] - (20 + qr_y + 20) * mm, "Organisateur : BdE INSA Lyon")
    p.drawString((20 + qr_x + 5) * mm, A4[0] - (20 + qr_y + 30) * mm, "Acheteur : {} {}".format(buyer_last_name, buyer_first_name))
    p.drawString((20 + qr_x + 5) * mm, A4[0] - (20 + qr_y + 40) * mm, "Date de commande : {}".format(order_date))
    p.drawString((20 + qr_x + 5) * mm, A4[0] - (20 + qr_y + 50) * mm, "Numéro de commande : {}".format(order))
    p.drawString((20 + qr_x + 5) * mm, A4[0] - (20 + qr_y + 60) * mm, "Valable pour : 1 personne")
    p.drawImage("ticketgenerator/bde.png", A4[1] - (20 + 22.53) * mm, A4[0] - (20 + 30) * mm, width=22.53 * mm,
                height=30 * mm, mask=None)
    p.drawString(90 * mm, 20 * mm,
                 "Billet vendu et édité par le BdE INSA Lyon, 20 avenue Albert Einstein, 69621 Villeurbanne CEDEX")
    # Close the PDF object cleanly.
    p.showPage()
    p.save()

    return response
