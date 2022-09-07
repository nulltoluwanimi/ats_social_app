from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django import forms

from .models import User


class CustomUserForm(UserCreationForm):
    class Meta:
        model = User
        exclude = ("password", "last_login")


class UserEditForm(UserChangeForm):
    full_name = forms.CharField(widget=forms.TextInput
                            (attrs={'placeholder': f'Full name', 'class':
                                    'border rounded-[10px] w-[483px] h-[43px] pl-[20px] mt-[5px] bg-[#FBFBFB] outline-none '}))
    phone_number = forms.CharField(widget=forms.TextInput
                            (attrs={'placeholder': f'Phone number', 'class':
                                    'border rounded-[10px] w-[483px] h-[43px] pl-[20px] mt-[5px] bg-[#FBFBFB] outline-none '}))

    class Meta:
        model = User
        fields = ("full_name", "profile_picture",
                  "phone_number", "nationality")
