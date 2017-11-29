from django.conf.urls import url, include
from rest_framework_jwt.views import obtain_jwt_token, refresh_jwt_token
from rest_framework_nested import routers
from . import views

router = routers.SimpleRouter()
router.register(r'events', views.EventsViewSet)
router.register(r'products', views.ProductViewSet, 'products')
router.register(r'options', views.OptionViewSet, 'options')
router.register(r'billets', views.BilletViewSet, 'billet')
router.register(r'order', views.OrderViewSet, 'orders')
# Wire up our API using automatic URL routing.
# Additionally, we include login URLs for the browsable API.
urlpatterns = [
    url(r'^authenticate/invitation$', views.InvitationAuthentication.as_view()),
    url(r'^authenticate$', obtain_jwt_token),
    url(r'^authenticate/refresh$', refresh_jwt_token),
    url(r'^', include(router.urls)),
    url(r'^rules', views.RulesViews.as_view()),
    url(r'^orders/(?P<id>[0-9]+)/final', views.OrderFinalViews.as_view()),
    url(r'^', include('rest_framework.urls', namespace='rest_framework')),

]
