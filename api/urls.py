from django.conf.urls import url, include
from rest_framework_jwt.views import obtain_jwt_token, refresh_jwt_token
from rest_framework_nested import routers
from . import views
from . import views_admin as admin

router = routers.SimpleRouter()
router.register(r'events', views.EventsViewSet)
router.register(r'products', views.ProductViewSet, 'products')
router.register(r'options', views.OptionViewSet, 'options')
router.register(r'billets', views.BilletViewSet, 'billet')
router.register(r'order', views.OrderViewSet, 'orders')

admin_router = routers.SimpleRouter()
admin_router.register(r'events', admin.EventViewSet, 'events')
admin_router.register(r'organizers', admin.OrganizerViewSet, 'organizers')
admin_router.register(r'invitations', admin.InvitationViewSet, 'invitations')
admin_router.register(r'billets', admin.BilletsViewSet, 'billets-admin')
admin_router.register(r'orders', admin.OrdersViewSet, 'orders-admin')

# Wire up our API using automatic URL routing.
# Additionally, we include login URLs for the browsable API.
urlpatterns = [
    url(r'^authenticate/invitation$', views.InvitationAuthentication.as_view()),
    url(r'^authenticate$', obtain_jwt_token),
    url(r'^authenticate/refresh$', refresh_jwt_token),
    url(r'^authenticate/logout$', views.LogoutViews.as_view()),
    url(r'^', include(router.urls)),
    url(r'^admin/', include(admin_router.urls, namespace='api_admin')),
    url(r'^rules', views.RulesViews.as_view()),
    url(r'^me', views.CurrentUserViews.as_view()),
    url(r'^', include('rest_framework.urls', namespace='rest_framework')),

]
