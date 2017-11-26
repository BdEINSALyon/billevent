from django.shortcuts import render

# Create your views here.
from django.http import HttpResponseNotFound
from reportlab.lib.pagesizes import A4, landscape
from reportlab.pdfgen import canvas
from django.http import HttpResponse
from reportlab.lib.units import mm
from reportlab.graphics.barcode import eanbc, qr, usps
from reportlab.graphics.shapes import Drawing
from reportlab.graphics import renderPDF
from api.models import Billet, Event

def generate_ticket(request):
    uid = "12345678"
    billet = Billet.objects.get(id=1)
    participants = billet.participants.all()
    order = billet.order
    product = billet.product
    client = order.client
    event = Event.objects.get(name = "Gala 22 - INSA Lyon")
    organizer = event.organizer

    if order.status != 5:
        return HttpResponseNotFound('<h1>Page not found</h1>')
    # Create the HttpResponse object with the appropriate PDF headers.
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="ticket.pdf"'

    # Create the PDF object, using the response object as its "file."
    p = canvas.Canvas(response, pagesize=A4)

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
    p.drawImage("ticketgenerator/background.png", 0 * mm, 0 * mm, width=210*mm, height=373*mm, mask=None)
    p.setFont("Helvetica", 12)
    p.setStrokeColorRGB(255, 255,255)
    p.setFillColorRGB(255, 255, 255)
    p.rect(20 * mm, A4[1] - 20 * mm - qr_y, qr_x - qr_width, qr_y, stroke=0, fill=1)
    d = Drawing(50, 10)
    d.add(barcode)
    renderPDF.draw(d, p, 20 * mm, A4[1] - 20 * mm - ba_height)
    d = Drawing(45, 45)
    d.add(qr_code)
    renderPDF.draw(d, p, 20 * mm + 0.5 * ba_width - 0.5 * qr_width, A4[1] - 20 * mm - qr_y)
    i = -20
    for participant in participants:
        i += 20
        p.drawString(20 * mm, A4[1] - qr_y - (20 + i + 10) * mm, "{}".format(participant.last_name))
        p.drawString(20 * mm, A4[1] - qr_y - (20 + i + 20) * mm, "{}".format(participant.first_name))
    p.drawString(20 * mm, A4[1] - qr_y - (20 + i + 30) * mm, "Prix TTC : {} €".format(product.price_ttc))
    p.drawString(20 * mm, A4[1] - qr_y - (20 + i + 40) * mm, "Date d'émission : {}".format(order.updated_at))
    p.setFont("Helvetica-Bold", 25)
    p.drawString(ba_width + (20 + 5) * mm, A4[1] - (20 + 10) * mm, "{}".format(event.name))
    p.drawString(ba_width + (20 + 5) * mm, A4[1] - (20 + 10 + 15) * mm, "{} - {}".format(event.start_time, event.end_time))
    p.drawString(ba_width + (20 + 5) * mm, A4[1] - (20 + 10 + 30) * mm, "{}".format(event.place))
    p.setFont("Helvetica", 12)
    p.drawString(ba_width + (20 + 5) * mm, A4[1] - (20 + 10 + 40) * mm, "{}".format(event.address))
    p.drawString(ba_width + (20 + 50) * mm, A4[1] - qr_y - (20 + 10) * mm, "Numéro : {}".format(billet.id))
    p.drawString(ba_width + (20 + 50) * mm, A4[1] - qr_y - (20 + 20) * mm, "Organisateur : {}".format(organizer.name))
    p.drawString(ba_width + (20 + 50) * mm, A4[1] - qr_y - (20 + 30) * mm, "Acheteur : {} {}".format(client.last_name, client.first_name))
    p.drawString(ba_width + (20 + 50) * mm, A4[1] - qr_y - (20 + 40) * mm, "Date de commande : {}".format(order.created_at))
    p.drawString(ba_width + (20 + 50) * mm, A4[1] - qr_y - (20 + 50) * mm, "Numéro de commande : {}".format(order.id))
    p.drawString(ba_width + (20 + 50) * mm, A4[1] - qr_y - (20 + 60) * mm, "Valable pour : {} personnes".format(1 + int(i/20)))
    p.drawImage("ticketgenerator/bde.png", A4[0] - (20 + 22.53) * mm, A4[1] - (20 + 30) * mm, width=22.53 * mm, height=30 * mm, mask=None)
    p.drawString(20 * mm, 40 * mm, "Billet vendu et édité par le {}, {}".format(organizer.name, organizer.address))
    p.drawString(20 * mm, 30 * mm, "Tél : {}".format(organizer.phone))
    p.drawString(20 * mm, 20 * mm, "Courriel : {}".format(organizer.email))
    # Close the PDF object cleanly.
    p.showPage()
    p.save()

    return response
