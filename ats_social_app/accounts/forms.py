from django.contrib.auth.forms import UserCreationForm


from .models import User



class CustomUserForm(UserCreationForm):
    class Meta:
        model = User
        exclude = ("password", "last_login")
        
