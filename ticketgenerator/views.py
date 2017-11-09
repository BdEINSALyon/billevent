from django.shortcuts import render

# Create your views here.
from reportlab.lib.pagesizes import A4, landscape
from reportlab.pdfgen import canvas
from django.http import HttpResponse
from reportlab.lib.units import mm
from reportlab.graphics.barcode import eanbc, qr, usps
from reportlab.graphics.shapes import Drawing
from reportlab.graphics import renderPDF

def generate_ticket(request):
    uid = "12345678"
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
    barcode = eanbc.Ean13BarcodeWidget(uid)
    ba_bounds = barcode.getBounds()
    ba_width = ba_bounds[2] - ba_bounds[0]
    ba_height = ba_bounds[3] - ba_bounds[1]
    qr_code = qr.QrCodeWidget(uid)
    qr_bounds = qr_code.getBounds()
    qr_width = qr_bounds[2] - qr_bounds[0]
    qr_height = qr_bounds[3] - qr_bounds[1]
    qr_x = ba_width + qr_width
    qr_y = ba_height + qr_height
    p.drawImage("ticketgenerator/background.png", 0 * mm, 0 * mm, width=373*mm, height=210*mm, mask=None)
    p.setFont("Helvetica", 12)
    p.setStrokeColorRGB(255, 255,255)
    p.setFillColorRGB(255, 255, 255)
    p.rect(20 * mm, A4[0] - 20 * mm - qr_y, qr_x - qr_width, qr_y, stroke=0, fill=1)
    d = Drawing(50, 10)
    d.add(barcode)
    renderPDF.draw(d, p, 20 * mm, A4[0] - 20 * mm - ba_height)
    d = Drawing(45, 45)
    d.add(qr_code)
    renderPDF.draw(d, p, 20 * mm, A4[0] - 20 * mm - qr_y)
    p.drawString(20 * mm, A4[0] - qr_y - (20 + 10) * mm, "{}".format(holder_last_name))
    p.drawString(20 * mm, A4[0] - qr_y - (20 + 20) * mm, "{}".format(holder_first_name))
    p.drawString(20 * mm, A4[0] - qr_y - (20 + 30) * mm, "Statut : {}".format(status))
    p.drawString(20 * mm, A4[0] - qr_y - (20 + 40) * mm, "Prix TTC : {} €".format(price))
    p.drawString(20 * mm, A4[0] - qr_y - (20 + 50) * mm, "Date d'émission : {}".format(issuing_date))
    p.setFont("Helvetica-Bold", 25)
    p.drawString(qr_x + (20 + 5) * mm, A4[0] - (20 + 10) * mm, "Gala INSA Lyon 2018")
    p.drawString(qr_x + (20 + 5) * mm, A4[0] - (20 + 10 + 15) * mm, "9 et 10 février")
    p.drawString(qr_x + (20 + 5) * mm, A4[0] - (20 + 10 + 30) * mm, "La sucrière")
    p.setFont("Helvetica", 12)
    p.drawString(qr_x + (20 + 5) * mm, A4[0] - (20 + 10 + 40) * mm, "49-50 Quai Rambaud 69002 Lyon - France")
    p.drawString(qr_x + (20 + 5) * mm, A4[0] - qr_y - (20 + 10) * mm, "Numéro : {}".format(uid))
    p.drawString(qr_x + (20 + 5) * mm, A4[0] - qr_y - (20 + 20) * mm, "Organisateur : BdE INSA Lyon")
    p.drawString(qr_x + (20 + 5) * mm, A4[0] - qr_y - (20 + 30) * mm, "Acheteur : {} {}".format(buyer_last_name, buyer_first_name))
    p.drawString(qr_x + (20 + 5) * mm, A4[0] - qr_y - (20 + 40) * mm, "Date de commande : {}".format(order_date))
    p.drawString(qr_x + (20 + 5) * mm, A4[0] - qr_y - (20 + 50) * mm, "Numéro de commande : {}".format(order))
    p.drawString(qr_x + (20 + 5) * mm, A4[0] - qr_y - (20 + 60) * mm, "Valable pour : 1 personne")
    p.drawImage("ticketgenerator/bde.png", A4[1] - (20 + 22.53) * mm, A4[0] - (20 + 30) * mm, width=22.53 * mm,
                height=30 * mm, mask=None)
    p.drawString(90 * mm, 20 * mm,
                 "Billet vendu et édité par le BdE INSA Lyon, 20 avenue Albert Einstein, 69621 Villeurbanne CEDEX")
    # Close the PDF object cleanly.
    p.showPage()
    p.save()

    return response
