from django.conf.urls.i18n import i18n_patterns
from django.contrib import admin
from django.urls import include, path
from django.conf.urls.static import static
from . import views
from django.conf import settings


urlpatterns = [
    path('i18n/', include('django.conf.urls.i18n')),
]
urlpatterns += i18n_patterns(
    path("securelogin/", admin.site.urls),
    path("", views.home, name="home"),
    path("store/", include("store.urls")),
    path("cart/", include("carts.urls")),
    path("accounts/", include("accounts.urls")),
    path("coupon/", include("coupon.urls")),
    path("order/", include("orders.urls")),
) + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
