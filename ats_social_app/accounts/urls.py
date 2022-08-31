from django.urls import path

from . import views

app_name = "accounts"

urlpatterns = [
    path("register/", views.sign_up, name="sign_up"),
    path("sign_in/", views.user_sign_in, name="sign_in"),
    path("sign_out/", views.user_sign_out, name="sign_out"),
    path("profile/<int:pk>/edit_details", views.user_edit_details, name="edit_details")
]