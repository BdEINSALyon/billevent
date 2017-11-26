from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^(?P<id>[0-9]+)/(?P<token>[0-9A-Za-z]+)$', views.MercanetViewSet.pay, name="mercanet-pay"),
    url(r'^check/([0-9]+)$', views.MercanetViewSet.check, name="mercanet-check-payment"),
    url(r'^auto/(.+)$', views.autoMercanet, name="mercanet-auto-payment"),
    url(r'^.+$', views.MercanetViewSet.error),
    url(r'^$', views.MercanetViewSet.error)
]