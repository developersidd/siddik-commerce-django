from django.urls import path
from . import views

urlpatterns = [
    path("", views.cart, name="cart"),
    path("checkout/", views.checkout, name="checkout"),
    path("add/<int:product_id>/", views.add_to_cart, name="add_to_cart"),
    path(
        "decrease/<int:product_id>/<int:cart_item_id>/",
        views.decrease_cart_item,
        name="decrease_cart_item",
    ),
    path(
        "remove/<int:product_id>/<int:cart_item_id>/",
        views.remove_cart_item,
        name="remove_cart_item",
    ),
]
