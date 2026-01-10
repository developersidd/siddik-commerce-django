from django.urls import path

from payment import views


urlpatterns = [
    path("ssl_payment", views.ssl_payment, name="ssl_payment"),
    path("validate_payment", views.validate_payment, name="validate_payment"),
    path("payment_success", views.payment_success, name="payment_success"),
    path("payment_failure", views.payment_failure, name="payment_failure"),
    path(
        "payment-failure-callback",
        views.payment_failure_callback,
        name="payment_failure_callback",
    ),
]
