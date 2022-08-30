from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .forms import CustomUserForm
from .models import User
# Register your models here.

class CustomUserAdmin(UserAdmin):
    form = CustomUserForm
    
    fieldsets = (
        ("Main Information", {"fields":("first_name","middle_name", "last_name", "nationality")}),
        ('None', {"fields":("email", "username", "phone_number")}),
        ("none", {"fields": ("date_of_birth", "profile_picture")})
    )
    
    list_display = ("first_name", "last_name", "email")
    ordering = ("username", )



admin.site.register(User, CustomUserAdmin)