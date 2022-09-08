from email.policy import default
from django.db import models

from accounts.models import User
from groups.models import Group, SuspendedMember, NotSuspendedMember

# Create your models here.


class StartedEvent(models.Manager):

    def get_queryset(self):
        return super().get_queryset().filter(is_started=True)


class NotStartedEvent(models.Manager):

    def get_queryset(self):
        return super().get_queryset().filter(is_started=False)


def _json():
    return dict


def _json_list():
    return list


class Notification(models.Model):
    user = models.ManyToManyField(User, null=True)
    group = models.ForeignKey(Group, on_delete=models.SET_NULL, null=True)
    content = models.TextField()
    time_stamp = models.DateTimeField(auto_now_add=True)
    is_admin_notification = models.BooleanField(default=False)


class Event(models.Model):
    creator = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    group = models.ForeignKey(Group, on_delete=models.SET_NULL, null=True)
    title = models.CharField(max_length=200)
    description = models.TextField()
    date_created = models.DateTimeField(auto_now_add=True)
    time_start = models.DateTimeField(null=True)
    time_end = models.DateTimeField(null=True)
    location = models.CharField(max_length=100, null=True, blank=True)
    is_started = models.BooleanField(default=False)
    yes = models.JSONField(default=_json_list(), null=True, blank=True)
    no = models.JSONField(default=_json_list(), null=True, blank=True)
    maybe = models.JSONField(default=_json_list(), null=True, blank=True)

    objects = models.Manager()
    started_objects = StartedEvent()
    running_objects = NotStartedEvent()


class Poll(models.Model):
    creator = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    group = models.ForeignKey(Group, on_delete=models.SET_NULL, null=True)
    title = models.CharField(max_length=90, null=True)
    description = models.TextField()
    start_date = models.DateTimeField()
    stop_date = models.DateTimeField()
    poll_option = models.JSONField(
        default=_json(), help_text="Maximum of 4 Options")
