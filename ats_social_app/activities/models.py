from email.policy import default
from django.db import models

from accounts.models import User
from groups.models import Groups

# Create your models here.

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
    

class Event(models.Model):
    creator = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    group = models.ForeignKey(Groups, on_delete=models.SET_NULL, null=True)
    title = models.CharField(max_length=200)
    description = models.TextField()
    date_created = models.DateTimeField(auto_now_add=True)
    time_start = models.DateTimeField(null=True)
    time_end = models.DateTimeField(null=True)
    # yes = models.JSONField(default=__json())
    # no = models.JSONField(default=__json())
    # maybe = models.JSONField(default=__json())
    
    
    
class Polls(models.Model):
    creator = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    group = models.ForeignKey(Groups, on_delete=models.SET_NULL, null=True)
    title = models.CharField(max_length=90, null=True)
    polls_option = models.JSONField(default=_json())
    
    
    