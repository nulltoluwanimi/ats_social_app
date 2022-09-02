from django.urls import path

from . import views

app_name = "groups"
urlpatterns = [
    path("", views.home, name='home'),
    path("<int:pk>/create-group/", views.create_group, name="create-group"),
    path('<int:pk>/group/<int:id>/', views.group_details, name="group"),
    path('<int:pk>/group/<int:id>/make_admin/<int:_id>', views.make_admin, name="make_admin"),
    path('<int:pk>/group/<int:id>/remove_admin/<int:_id>', views.remove_as_admin, name="remove_as_admin"),
    path('<int:pk>/group/<int:id>/suspend_member/<int:_id>', views.remove_as_admin, name="remove_as_admin"),
    path('<int:pk>/group/<int:id>/remove_member/<int:_id>', views.remove_member_of_group, name="remove_member"),
    
    path("<int:pk>/join-group/", views.join_group, name="join_group"),
    path("<int:pk>/group/<int:id>/exit_group", views.exit_group, name="exit_group"),
    
    path("<int:pk>/group/<int:id>/comment/<int:_id>/reply/", views.create_reply, name="create_reply"),
    
    path("<int:pk>/group/<int:id>/comment/<int:_id>/like/", views.like_comment, name="like_comment"),
    path("<int:pk>/group/<int:id>/reply/<int:_id>/like/", views.like_reply, name="like_reply"),
    path("<int:pk>/group/<int:id>/post/<int:_id>/like/", views.like_post, name="like_post"),
    
    
    path("<int:pk>/group/<int:id>/comment/<int:_id>/hide/", views.hide_comment, name="hide_comment"),
    path("<int:pk>/group/<int:id>/reply/<int:_id>/hide/", views.hide_reply, name="hide_reply"),
    path("<int:pk>/group/<int:id>/post/<int:_id>/hide/", views.hide_post, name="hide_post"),
    
   
]
