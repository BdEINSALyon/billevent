from django.conf import settings
from django.conf.urls import url
from django.conf.urls.static import static

from frontend import views

urlpatterns = [
    url(r'^$', views.VueAppView.as_view()),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
