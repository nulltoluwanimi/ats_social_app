from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils import timezone
from django.db import models

# Create your models here.


class Post(models.Model):
    title = models.CharField(max_length=255, blank=True)
    image = models.ImageField(upload_to='image/')
    date_posted = models.DateTimeField(default=timezone.now)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    tags = models.CharField(max_length=100, blank=True)
    active = models.BooleanField(default=True)
    likes = models.ManyToManyField(User, related_name='post_like', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

    def total_likes(self):
        return self.likes.count()

    def get_absolute_url(self):
        return reverse('post-detail', kwargs={'pk': self.pk})


class Comments(models.Model):
    post = models.ForeignKey(
        Post, related_name='postdetails', on_delete=models.CASCADE)
    user = models.ForeignKey(
        User, related_name='userdetails', on_delete=models.CASCADE)
    comment = models.CharField(max_length=255)
    comment_date = models.DateTimeField(default=timezone.now)
    parent = models.ForeignKey('self', null=True, blank=True,
                               related_name='replies',
                               on_delete=models.SET_NULL
                               )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
