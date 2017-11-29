from django.core.signing import TimestampSigner
from django.http import HttpResponse
import datetime

def getid(request, id):
    now = datetime.datetime.now()
    uid = TimestampSigner().sign(id)
    html = "<html><body>ID : %s à </body></html>" % uid + "<html><body>%s</body></html>" % now
    return HttpResponse(html)
