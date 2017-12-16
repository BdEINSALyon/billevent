from django.core.signing import Signer
from django.http import HttpResponse
from datetime import datetime

from django.utils.formats import date_format
from reportlab.graphics import renderPDF
from reportlab.lib.utils import ImageReader
from reportlab.graphics.barcode import eanbc, qr, code128
from reportlab.graphics.barcode.widgets import BarcodeCode128
from reportlab.graphics.shapes import Drawing
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas

from api.models import BilletOption


def generate(order):
    # Create the HttpResponse object with the appropriate PDF headers.
    response = HttpResponse(content_type='application/pdf')

    # Create the PDF object, using the response object as its "file."
    p = canvas.Canvas(response, pagesize=A4)

    client = order.client
    event = order.event
    organizer = event.organizer

    for billet in order.billets.all():
        # Draw things on the PDF. Here's where the PDF generation happens.
        # See the ReportLab documentation for the full list of functionality.
        price = 0
        uid = Signer().sign(billet.id)
        product = billet.product
        participants = billet.participants.all()
        if product:
            price = product.price_ttc

        barcode = BarcodeCode128(value=uid)
        ba_bounds = barcode.getBounds()
        ba_width = ba_bounds[2] - ba_bounds[0]
        ba_height = ba_bounds[3] - ba_bounds[1]
        qr_code = qr.QrCodeWidget(uid)
        qr_bounds = qr_code.getBounds()
        qr_width = qr_bounds[2] - qr_bounds[0]
        qr_height = qr_bounds[3] - qr_bounds[1]
        qr_y = ba_height + qr_height
        if event.ticket_background:
            p.drawImage(ImageReader(event.ticket_background), 0 * mm, 0 * mm, width=A4[0], height=A4[1],
                        mask='auto', preserveAspectRatio=False)
        p.setFont("Helvetica", 12)
        p.setStrokeColorRGB(255, 255, 255)
        p.setFillColorRGB(255, 255, 255)
        p.rect(20 * mm, A4[1] - 20 * mm - qr_y, ba_width, qr_y, stroke=1, fill=1)
        p.setStrokeColorRGB(0, 0, 0)
        p.setFillColorRGB(0, 0, 0)
        d = Drawing(50, 10)
        d.add(barcode)
        renderPDF.draw(d, p, 20 * mm, A4[1] - 20 * mm - ba_height)
        d = Drawing(45, 45)
        d.add(qr_code)
        renderPDF.draw(d, p, 20 * mm + 0.5 * ba_width - 0.5 * qr_width, A4[1] - 20 * mm - qr_y)
        options_number = 0
        i = -10
        for participant in participants:
            i += 10
            p.drawString(20 * mm, A4[1] - qr_y - (20 + i + 10) * mm,
                         "{} {}".format(participant.last_name, participant.first_name))
            billet_options = BilletOption.objects.filter(participant=participant)
            for billet_option in billet_options:
                options_number += 1
                i += 10
                option = billet_option.option
                option_name = option.name
                amount = billet_option.amount
                price += option.price_ttc * amount
                p.drawString((20 + 10) * mm, A4[1] - qr_y - (20 + i + 10) * mm,
                             "{} * {} : {} €".format(amount, option_name, option.price_ttc * amount))
        billet_options = BilletOption.objects.filter(billet=billet).exclude(participant__isnull=False)
        for billet_option in billet_options:
            options_number += 1
            i += 10
            option = billet_option.option
            option_name = option.name
            amount = billet_option.amount
            price += option.price_ttc * amount
            p.drawString(20 * mm, A4[1] - qr_y - (20 + i + 20) * mm,
                         "{} * {} : {} €".format(amount, option_name, option.price_ttc * amount))
        if product:
            i += 10
            p.setFont("Helvetica-Bold", 12)
            p.drawString(20 * mm, A4[1] - qr_y - (20 + i + 10) * mm,
                         "> {} : {} €".format(product.name, product.price_ttc))
        p.setFont("Helvetica", 12)
        p.drawString(20 * mm, A4[1] - qr_y - (20 + i + 30) * mm, "Prix TTC : {} €".format(price))
        p.drawString(20 * mm, A4[1] - qr_y - (20 + i + 40) * mm, "Date d'émission : {}".format(
            date_format(datetime.now(), "SHORT_DATE_FORMAT"))
                     )
        p.setFont("Helvetica-Bold", 20)
        p.drawString(ba_width + (20 + 5) * mm, A4[1] - (20 + 20) * mm, "{}".format(event.name))
        p.setFont("Helvetica-Bold", 16)
        p.drawString(ba_width + (20 + 5) * mm, A4[1] - (20 + 15 + 15) * mm, "{}".format(
            date_format(event.start_time.date(), "SHORT_DATE_FORMAT")))
        p.setFont("Helvetica", 12)
        p.drawString(ba_width + (20 + 5) * mm, A4[1] - (20 + 10 + 30) * mm, "{}".format(event.place))
        p.drawString(ba_width + (20 + 5) * mm, A4[1] - (20 + 10 + 40) * mm, "{}".format(event.address))
        p.drawString(ba_width + (20 + 8) * mm, A4[1] - qr_y - (20 + 20) * mm,
                     "Billet #{}-{}-{}".format(event.id, order.id, billet.id))
        p.drawString(ba_width + (20 + 8) * mm, A4[1] - qr_y - (20 + 30) * mm,
                     "Organisateur : {}".format(organizer.name))
        p.drawString(ba_width + (20 + 8) * mm, A4[1] - qr_y - (20 + 40) * mm,
                     "Acheteur : {} {}".format(client.last_name, client.first_name))
        if len(participants) > 0:
            validity = "personnes"
            persons_number = len(participants)
            if len(participants) < 2:
                validity = "personne"
        else:
            validity = "Options"
            persons_number = ""
            if options_number < 2:
                validity = "Option"
        p.drawString(ba_width + (20 + 8) * mm, A4[1] - qr_y - (20 + 50) * mm,
                     "Valable pour : {} {}".format(persons_number, validity))
        p.drawString(20 * mm, 40 * mm, "Billet vendu et édité par : {}, {}".format(organizer.name, organizer.address))
        p.drawString(20 * mm, 30 * mm, "Tél : {}".format(organizer.phone))
        p.drawString(20 * mm, 20 * mm, "Courriel : {}".format(organizer.email))
        # Close the PDF object cleanly.
        p.showPage()

    p.save()
    return response
