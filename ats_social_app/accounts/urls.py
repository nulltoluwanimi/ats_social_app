from django.urls import path

from . import views

app_name = "accounts"
urlpatterns = [
    path("", views.home, name='home'),
    path("sign_up/", views.sign_up, name="sign_up"),
    path("sign_in/", views.user_sign_in, name="sign_in"),
    path("sign_out/", views.user_sign_out, name="sign_out"),
    path("profile/<int:pk>/edit_details",
         views.user_edit_details, name="edit_details"),
    path('profile/<int:pk>/', views.UserProfile.as_view(), name="profile"),
    path('reset-password/', views.RecoverPassword.as_view(), name='reset-password'),
    path('password-token/<str:uid>/<str:token>/',
         views.ResetPassword.as_view(), name='set-password'),

]
