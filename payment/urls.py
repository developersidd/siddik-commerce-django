from django.urls import path

from payment import views


urlpatterns = [
    path("ssl_payment", views.ssl_payment, name="ssl_payment"),
    path("validate_payment", views.validate_payment, name="validate_payment"),
    path("payment_success", views.payment_success, name="payment_success"),
]
