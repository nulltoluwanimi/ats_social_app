from multiprocessing.spawn import old_main_modules
from django.db import models

from accounts.models import User


class ActiveManager(models.Manager):
    
    def get_queryset(self):
        return super().get_queryset().filter(is_active=True)
    

class InactiveManager(models.Manager):
    
    def get_queryset(self):
        return super().get_queryset().filter(is_active=False)



class Groups(models.Model):
    owner = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name="group_creator")
    name_of_group = models.CharField(max_length=500, null=True)
    picture = models.ImageField(null=True, upload_to="group_images")
    title = models.CharField(max_length=50, null=True)
    description = models.TextField(null=True)
    date_created = models.DateTimeField(auto_now_add=True)
    is_closed = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    
    
    objects = models.Manager()
    active_objects = ActiveManager()
    inactive_objects = InactiveManager()
    
class Members(models.Model):
    group = models.ForeignKey(Groups, on_delete=models.CASCADE)
    member = models.ForeignKey(User, on_delete=models.CASCADE)
    is_admin = models.BooleanField(default=True)
    is_suspended = models.BooleanField(default=False)
    


class Posts(models.Model):
    member = models.ForeignKey(Members, on_delete=models.SET_NULL, null=True)
    group = models.ForeignKey(Groups, on_delete=models.SET_NULL, null=True)
    title = models.CharField(max_length=50, null=True)
    body = models.TextField()
    image = models.ImageField(blank=True, upload_to="post_images", null=True)
    additional_files = models.FileField(blank=True, upload_to="post_files", null=True)
    date_created = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    
    objects = models.Manager()
    active_objects = ActiveManager()
    inactive_objects = InactiveManager()


class Comments(models.Model):
    member = models.ForeignKey(Members, on_delete=models.SET_NULL, null=True)
    post = models.ForeignKey(Posts, on_delete=models.SET_NULL, null=True)
    content = models.TextField()
    date_created = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    
    objects = models.Manager()
    active_objects = ActiveManager()
    inactive_objects = InactiveManager()
    

class Replies(models.Model):
    member = models.ForeignKey(Members, on_delete=models.SET_NULL, null=True)
    comment = models.ForeignKey(Comments, on_delete=models.SET_NULL, null=True)
    content = models.TextField()
    date_created = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    
    objects = models.Manager()
    active_objects = ActiveManager()
    inactive_objects = InactiveManager()
    
    
class Likes(models.Model):
    member = models.ForeignKey(Members, on_delete=models.SET_NULL, null=True)
    comment = models.ForeignKey(Comments, blank=True, null=True, on_delete=models.SET_NULL)
    reply = models.ForeignKey(Replies, blank=True, null=True, on_delete=models.SET_NULL)
    date_created = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    
    objects = models.Manager()
    active_objects = ActiveManager()
    inactive_objects = InactiveManager()
    


    
    
    