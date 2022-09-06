from django.urls import path

from . import views

app_name = "groups"
urlpatterns = [
    path("create-group/<int:pk>/", views.create_group, name="create-group"),
    path('group/<int:pk>/<str:type>', views.group_details, name="group"),
    path("<int:pk>/group_request/<int:id>/", views.accept_request_closed_group, name="join_closed_group"),
    path("<int:pk>/group_request/<int:id>/", views.reject_request_closed_group, name="reject_closed_group")

    # path("register/", views.sign_up, name="sign_up"),
    # path("sign_in/", views.user_sign_in, name="sign_in"),
    # path("sign_out/", views.user_sign_out, name="sign_out"),
    # path("profile/<int:pk>/edit_details",
    #      views.user_edit_details, name="edit_details")
]
