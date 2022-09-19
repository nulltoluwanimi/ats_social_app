from re import T
from django.db import models

from django.contrib.auth import get_user_model
from django_ckeditor_5.fields import CKEditor5Field

from accounts.models import User


class ActiveManager(models.Manager):

    def get_queryset(self):
        return super().get_queryset().filter(is_active=True)


class InactiveManager(models.Manager):

    def get_queryset(self):
        return super().get_queryset().filter(is_active=False)


class SuspendedMember(models.Manager):

    def get_queryset(self):
        return super().get_queryset().filter(is_suspended=True, is_active=True)


class NotSuspendedMember(models.Manager):

    def get_queryset(self):
        return super().get_queryset().filter(is_suspended=False, is_active=True)


class Group(models.Model):
    owner = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, related_name="group_creator")
    name_of_group = models.CharField(max_length=500, null=True)
    picture = models.ImageField(
        null=True, upload_to="group_images", blank=True)
    title = models.CharField(max_length=50, null=True)
    description = models.TextField(null=True)
    date_created = models.DateTimeField(auto_now_add=True)
    is_closed = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    objects = models.Manager()
    active_objects = ActiveManager()
    inactive_objects = InactiveManager()

    def __str__(self) -> str:
        return f'{self.name_of_group}'

    class Meta:
        verbose_name = 'group'
        verbose_name_plural = 'groups'


class GroupRequest(models.Model):
    STATUS_CHOICES = (
        ("ACCEPTED", "ACCEPTED"),
        ("REJECTED", "REJECTED"),
        ("INITIATED", "INITIATED"),
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    group = models.ForeignKey(Group, on_delete=models.CASCADE)
    request_message = models.TextField()
    status = models.CharField(choices=STATUS_CHOICES,
                              max_length=15, null=True, default="INITIATED")
    time_stamp = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    objects = models.Manager()
    active_objects = ActiveManager()
    inactive_objects = InactiveManager()

    class Meta:
        unique_together = ("user", "group", "is_active")


class Members(models.Model):
    group = models.ForeignKey(Group, on_delete=models.CASCADE)
    member = models.ForeignKey(User, on_delete=models.CASCADE)
    is_admin = models.BooleanField(default=False)
    is_suspended = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    objects = models.Manager()
    active_objects = ActiveManager()
    inactive_objects = InactiveManager()
    suspended_objects = SuspendedMember()
    not_suspended_objects = NotSuspendedMember()

    def __str__(self):
        return self.member.username

    class Meta:
        verbose_name = 'member'
        verbose_name_plural = 'members'
        unique_together = ("group", "member", "is_active")


class Posts(models.Model):
    member = models.ForeignKey(Members, on_delete=models.SET_NULL, null=True)
    group = models.ForeignKey(Group, on_delete=models.SET_NULL, null=True)
    title = models.CharField(max_length=50, null=True,
                             blank=True, default=group.name)
    body = CKEditor5Field('body', config_name="extends")
    image = models.ImageField(blank=True, upload_to="post_images", null=True)
    additional_files = models.FileField(
        blank=True, upload_to="post_files", null=True)
    date_created = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    objects = models.Manager()
    active_objects = ActiveManager()
    inactive_objects = InactiveManager()

    class Meta:
        verbose_name = 'post'
        verbose_name_plural = 'posts'
        ordering = ('-date_created',)

    def __str__(self):
        return self.title


class Comments(models.Model):
    member = models.ForeignKey(Members, on_delete=models.SET_NULL, null=True)
    post = models.ForeignKey(Posts, on_delete=models.SET_NULL, null=True)
    content = models.TextField()
    date_created = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    objects = models.Manager()
    active_objects = ActiveManager()
    inactive_objects = InactiveManager()

    class Meta:
        verbose_name = 'comment'
        verbose_name_plural = 'comments'
        ordering = ("-date_created",)

    def __str__(self):
        return self.post.title


class Replies(models.Model):
    member = models.ForeignKey(Members, on_delete=models.SET_NULL, null=True)
    comment = models.ForeignKey(Comments, on_delete=models.SET_NULL, null=True)
    content = models.TextField()
    date_created = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    objects = models.Manager()
    active_objects = ActiveManager()
    inactive_objects = InactiveManager()

    class Meta:
        verbose_name = 'replies'
        verbose_name_plural = 'replies'
        ordering = ("-date_created",)

    def __str__(self):
        return self.comment


class Likes(models.Model):
    member = models.ForeignKey(Members, on_delete=models.SET_NULL, null=True)
    post = models.ForeignKey(
        Posts, on_delete=models.SET_NULL, null=True, blank=True)
    comment = models.ForeignKey(
        Comments, blank=True, null=True, on_delete=models.SET_NULL)
    reply = models.ForeignKey(
        Replies, blank=True, null=True, on_delete=models.SET_NULL)
    date_created = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=False)

    objects = models.Manager()
    active_objects = ActiveManager()
    inactive_objects = InactiveManager()

    class Meta:
        verbose_name = 'like'
        verbose_name_plural = 'likes'
        ordering = ("-date_created",)

    def __str__(self):
        return str(self.member)
