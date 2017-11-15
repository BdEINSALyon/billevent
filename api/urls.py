from django.conf.urls import url, include
from rest_framework_jwt.views import obtain_jwt_token, refresh_jwt_token
from rest_framework_nested import routers
from . import views

router = routers.SimpleRouter()
router.register(r'events', views.EventsViewSet)
router.register(r'options', views.OptionViewSet)


# Wire up our API using automatic URL routing.
# Additionally, we include login URLs for the browsable API.
urlpatterns = [
    url(r'^token-auth/', obtain_jwt_token),
    url(r'^token-refresh/', refresh_jwt_token),
    url(r'^', include(router.urls)),
    url(r'^', include('rest_framework.urls', namespace='rest_framework')),
]

