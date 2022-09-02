from django.contrib.auth.forms import UserCreationForm, UserChangeForm


from .models import User


class CustomUserForm(UserCreationForm):
    class Meta:
        model = User
        exclude = ("password", "last_login")


class UserEditForm(UserChangeForm):
    class Meta:
        model = User
        fields = ("full_name", "profile_picture",
                  "phone_number", "nationality")
