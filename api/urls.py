from django.conf.urls import url, include
from rest_framework_jwt.views import obtain_jwt_token, refresh_jwt_token
from rest_framework_nested import routers
from . import views

router = routers.SimpleRouter()
router.register(r'events', views.EventsViewSet)

# Wire up our API using automatic URL routing.
# Additionally, we include login URLs for the browsable API.
urlpatterns = [
    url(r'^token-auth/', obtain_jwt_token),
    url(r'^token-refresh/', refresh_jwt_token),
    url(r'^', include(router.urls)),
    url(r'^', include('rest_framework.urls', namespace='rest_framework')),

    #Products Endpoints
    url(r'products/list/(?P<event>[0-9]+)',views.products_list, name="product-list"),
    url(r'products/(?P<id>[0-9]+)$',views.products_by_id,name="product-by-id"),
    url(r'products/(?P<product_id>[0-9]+)/canBuyOneMore',views.canBuyOneMoreProduct,name="can-buy-one"),

    #Options EndPoints
    url(r'options/(?P<id>[0-9]+)$', views.option_by_id, name="product-by-id"),
    url(r'options/(?P<option_id>[0-9]+)/canBuyOneMore', views.canBuyOneMoreOption, name="can-buy-one"),

    #url(r'options/question/')
    url(r'options/byProduct/(?P<product_id>[0-9]+)', views.option_by_product, name="option-by-product"),

]

