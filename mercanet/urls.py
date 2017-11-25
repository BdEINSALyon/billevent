from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^([0-9]+)$', views.MercanetViewSet.pay),
    url(r'^([0-9]+)/check/$', views.MercanetViewSet.check),
    url(r'^auto/(.+)$', views.MercanetViewSet.autoMercanet),
    url(r'^.+$', views.MercanetViewSet.error),
    url(r'^$', views.MercanetViewSet.error)
]