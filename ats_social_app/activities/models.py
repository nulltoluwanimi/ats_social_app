from email.policy import default
from django.db import models

from accounts.models import User
from groups.models import Groups, SuspendedMember, NotSuspendedMember

# Create your models here.

class StartedEvents(models.Manager):
    
    def get_queryset(self):
        return super().get_queryset().filter(is_started=True)
    
    
class NotStartedEvents(models.Manager):
    
    def get_queryset(self):
        return super().get_queryset().filter(is_started=False)
    
    

def _json():
    return dict

def __json():
    return list


class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    group = models.ForeignKey(Groups, on_delete=models.SET_NULL, null=True)
    content = models.TextField()
    time_stamp = models.DateTimeField(auto_now_add=True)
    is_admin_notification = models.BooleanField(default=True)
    

class Events(models.Model):
    creator = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    group = models.ForeignKey(Groups, on_delete=models.SET_NULL, null=True)
    title = models.CharField(max_length=200)
    description = models.TextField()
    date_created = models.DateTimeField(auto_now_add=True)
    time_start = models.DateTimeField(null=True)
    time_end = models.DateTimeField(null=True)
    location = models.CharField(max_length=100, null=True, blank=True)
    is_started = models.BooleanField(default=False)
    yes = models.JSONField(default=__json())
    no = models.JSONField(default=__json())
    maybe = models.JSONField(default=__json())
    
    
    objects = models.Manager()
    started_objects = StartedEvents()
    running_objects = NotStartedEvents()
    
    
    
class Polls(models.Model):
    creator = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    group = models.ForeignKey(Groups, on_delete=models.SET_NULL, null=True)
    title = models.CharField(max_length=90, null=True)
    start_date = models.DateTimeField()
    stop_date = models.DateTimeField()
    polls_option = models.JSONField(default=_json(), help_text="Maximum of 4 Options")
    
    
    