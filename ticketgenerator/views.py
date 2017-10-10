from django.shortcuts import render

# Create your views here.
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from django.http import HttpResponse

def generate_ticket(request):
    # Create the HttpResponse object with the appropriate PDF headers.
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="ticket.pdf"'

    # Create the PDF object, using the response object as its "file."
    p = canvas.Canvas(response, pagesize=A4)

    # Draw things on the PDF. Here's where the PDF generation happens.
    # See the ReportLab documentation for the full list of functionality.
    p.drawString(50, 800, "Hello world. ")
    p.drawImage("ticketgenerator/views.py", 0,0, width=None,height=None,mask=None)


    # Close the PDF object cleanly.
    p.showPage()
    p.save()

    return response
