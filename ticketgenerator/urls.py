from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^(?P<id>[0-9A-Za-z-:]+)/ticket$', views.generate_ticket),
]
