from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^?amount=(?P<amount>[0-9]+{10}$', views.MercanetViewSet),
]