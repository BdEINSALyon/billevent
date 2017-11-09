from reportlab.lib.units import mm
from reportlab.graphics.barcode import createBarcodeDrawing
from reportlab.graphics.shapes import Drawing, String
from reportlab.graphics.charts.barcharts import HorizontalBarChart


def barcodemescouilles(codename, qr_x, *args, **kw):
    barcode = createBarcodeDrawing('Code128', value=codename, barHeight=qr_x * mm, humanReadable=True)
    return barcode.asString('gif')



