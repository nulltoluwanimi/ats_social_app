from django.urls import path
from . import views


app_name = "activities"

urlpatterns = [
    path("<int:pk>/group/<int:id>/create_event",
         views.create_event, name="create_event"),
    path("<int:pk>/group/<int:id>/create_event/<int:_id>",
         views.edit_event, name="edit_event"),
    path("<int:pk>/group/<int:id>/event_list",
         views.EventList.as_view(), name="event_list"),
    # <<<<<<< HEAD
    #     path("<int:pk>/group/<int:id>/create_event/<int:_id>/accept", views.accept_invite, name="accept_invite"),
    #     path("<int:pk>/group/<int:id>/create_event/<int:_id>/reject", views.reject_invite, name="reject_invite"),
    #     path("<int:pk>/group/<int:id>/create_event/<int:_id>/inconclusive", views.inconclusive_decision_invite,
    # =======
    path("<int:pk>/group/<int:id>/create_event/<int:_id>/accept/<int:__id>",
         views.accept_invite, name="accept_invite"),
    path("<int:pk>/group/<int:id>/create_event/<int:_id>/reject/<int:__id>",
         views.reject_invite, name="reject_invite"),
    path("<int:pk>/group/<int:id>/create_event/<int:_id>/inconclusive/<int:__id>", views.inconclusive_decision_invite,

         name="maybe_invite"),
    path("<int:pk>/group/<int:id>/event_list",
         views.AdminAllGroupEvents.as_view(), name="event_list"),
    path("<int:pk>/group/<int:id>/event_detail",
         views.AdminEventDetail.as_view(), name="event_detail"),

    path("<int:pk>/group/<int:id>/create_polls",
         views.create_polls, name="create_polls"),
    # <<<<<<< HEAD
    #     path("<int:pk>/group/<int:id>/polls/vote_option_1", views.polls_option1, name="vote_option_1"),
    #     path("<int:pk>/group/<int:id>/polls/vote_option_2", views.polls_option2, name="vote_option_2"),
    #     path("<int:pk>/group/<int:id>/polls/vote_option_3", views.polls_option3, name="vote_option_3"),
    #     path("<int:pk>/group/<int:id>/polls/vote_option_4", views.polls_option4, name="vote_option_4"),
    # =======
    path("<int:pk>/group/<int:id>/polls/vote_option_1",
         views.poll_option_1, name="vote_option_1"),
    path("<int:pk>/group/<int:id>/polls/vote_option_2",
         views.poll_option_2, name="vote_option_2"),
    path("<int:pk>/group/<int:id>/polls/vote_option_3",
         views.poll_option_3, name="vote_option_3"),
    path("<int:pk>/group/<int:id>/polls/vote_option_4",
         views.poll_option_4, name="vote_option_4"),


]
