from django.urls import path
from . import views

urlpatterns = [
    path("register/", views.register, name="register"),
    path("login/", views.login, name="login"),
    path("activate/<uidb64>/<token>/", views.activate_account, name="activate"),
    path("logout/", views.logout, name="logout"),
    path("email_template/", views.email_template, name="email_template"),
]
