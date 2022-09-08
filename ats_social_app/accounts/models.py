from django.db import models
from django.contrib.auth.models import AbstractUser
from phonenumber_field.modelfields import PhoneNumberField
# Create your models here.


class User(AbstractUser):
    full_name = models.CharField(max_length=100, null=True, blank=True)
    email = models.EmailField(unique=True)
    username = models.CharField(max_length=20, unique=True)
    date_of_birth = models.DateField(null=True, blank=True,)
    profile_picture = models.ImageField(
        upload_to='profile_pictures', default="profile_pictures/avatar.svg")
    phone_number = PhoneNumberField(unique=True, null=True, blank=True)
    nationality = models.CharField(max_length=30, blank=True, null=True)
    is_verified = models.BooleanField(default=False)
    date_joined = models.DateField(auto_now=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ['username', ]

    def __str__(self):
        return self.username
