from django.urls import path
from coupon import views

urlpatterns = [path("apply/", views.apply_coupon, name="apply_coupon")]
