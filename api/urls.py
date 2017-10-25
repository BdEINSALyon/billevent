from django.conf.urls import url, include
from rest_framework_nested import routers
from . import views

router = routers.SimpleRouter()
router.register(r'users', views.UserViewSet)
router.register(r'groups', views.GroupViewSet)
router.register(r'events', views.EventsViewSet)

events_router = routers.NestedSimpleRouter(router, r'events', lookup='events')
#events_router.register(r'')

# Wire up our API using automatic URL routing.
# Additionally, we include login URLs for the browsable API.
urlpatterns = [
    url(r'^api/', include(router.urls)),
    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework'))
]