from django.conf.urls import url
from . import views

urlpatterns = [
   # url(r'^check/([0-9]+)$', views.MercanetViewSet.check, name="mercanet-check-payment"),
    url(r'^yes$', views.MercanetViewSet.pay, name="mercanet-pay"),
    url(r'^auto/$', views.autoMercanet, name="mercanet-auto-payment"),
]
