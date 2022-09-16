from email.policy import default
from django.db import models

from accounts.models import User
from groups.models import Group, SuspendedMember, NotSuspendedMember, Posts, Replies, Likes, Members, InactiveManager, \
    ActiveManager


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
    user = models.ManyToManyField(User, related_name="notification_users")
    group = models.ForeignKey(Group, on_delete=models.SET_NULL, null=True, blank=True)
    title = models.TextField()
    content = models.TextField()
    time_stamp = models.DateTimeField(auto_now_add=True)
    is_admin_notification = models.BooleanField(default=False)

    class Meta:
        ordering = ('-time_stamp',)

    def __str__(self):
        return self.title


class Event(models.Model):
    creator = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    group = models.ForeignKey(Group, on_delete=models.SET_NULL, null=True)
    title = models.CharField(max_length=200)
    description = models.CharField(max_length=500, null=True)
    date_created = models.DateTimeField(auto_now_add=True)
    time_start = models.DateTimeField(null=True)
    time_end = models.DateTimeField(null=True)
    location = models.CharField(max_length=100, null=True)
    is_started = models.BooleanField(default=False)
    yes = models.JSONField(default=_json_list(), null=True, blank=True)
    no = models.JSONField(default=_json_list(), null=True, blank=True)
    maybe = models.JSONField(default=_json_list(), null=True, blank=True)

    # yes = models.ManyToManyField(User, related_name="event_yes")
    # no = models.ManyToManyField(User, related_name="event_no")
    # maybe = models.ManyToManyField(User, related_name="event_maybe")

    objects = models.Manager()
    started_objects = StartedEvent()
    running_objects = NotStartedEvent()

    class Meta:
        ordering = ("-date_created",)

    def for_yes(self):
        return len(self.yes)

    def for_no(self):
        return len(self.no)

    def for_maybe(self):
        return len(self.maybe)

    def __str__(self):
        return self.title


class EventInvite(models.Model):
    member = models.ForeignKey(Members, on_delete=models.CASCADE)
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    is_active = models.BooleanField(default=True)
    # date_created = models.DateTimeField(auto_now_add=True)

    objects = models.Manager()
    active_objects = ActiveManager()
    inactive_objects = InactiveManager()

    # class Meta:
    #     ordering = ("-date_created",)


class Poll(models.Model):
    creator = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    group = models.ForeignKey(Group, on_delete=models.SET_NULL, null=True)
    title = models.CharField(max_length=90, null=True, help_text="Kindly input the question")
    description = models.CharField(max_length=500)

    start_date = models.DateTimeField()
    stop_date = models.DateTimeField()
    poll_option = models.JSONField(
        default=_json(), help_text="Maximum of 4 Options")

    # poll_option_1_tag = models.CharField(max_length=40, null=True, blank=True)
    # poll_option_2_tag = models.CharField(max_length=40, null=True, blank=True)
    # poll_option_3_tag = models.CharField(max_length=40, null=True, blank=True)
    # poll_option_4_tag = models.CharField(max_length=40, null=True, blank=True)
    #
    # poll_option_1_count = models.ManyToManyField(User, related_name="poll_1")
    # poll_option_2_count = models.ManyToManyField(User, related_name="poll_2")
    # poll_option_3_count = models.ManyToManyField(User, related_name="poll_3")
    # poll_option_4_count = models.ManyToManyField(User, related_name="poll_4")
