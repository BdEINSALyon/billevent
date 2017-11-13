from django.conf.urls import url, include
from rest_framework_nested import routers
from . import views

router = routers.SimpleRouter()
router.register(r'events', views.EventsViewSet)
router.register(r'options', views.OptionViewSet, "AHHHHHHH")

# Wire up our API using automatic URL routing.
# Additionally, we include login URLs for the browsable API.
urlpatterns = [
    url(r'^/', include(router.urls)),
    url(r'^/', include('rest_framework.urls', namespace='rest_framework'))
]
