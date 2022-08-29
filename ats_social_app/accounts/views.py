from django.shortcuts import render
from django.contrib.auth import login, logout, authenticate, update_session_auth_hash
from django.contrib import messages
from django.views.generic import DetailView
from django.contrib.auth.forms import PasswordChangeForm


from .forms import CustomUserForm
from .models import User

# Create your views here.


def sign_up(request):
    form = CustomUserForm
    page = "register"
    
    if request.method == "POST":
        form = CustomUserForm(request.POST, request.FILES)
        
        if form.is_valid():
            custom_user = form.save(commit=False)
            custom_user.save()
            
            # login(request, custom_user)
            # USER NEEDS TO VERIFY MAIL
            return
            
        else:
            messages.error(request, 'Invalid detail entered, kindly check')
            return
            
        
    
    context = {"form": form,
               "page":page
               }
    return render(request, "accounts/login_register.html", context)


def user_sign_in(request):
    email = request.method.get("email")
    password = request.method.get("password")
    
    try:
        user = User.objects.get(email=email.lower())
        
    except User.DoesNotExist:
        messages.error(request, "Invalid Email")
        return
    
    user = authenticate(email=email, password=password)
    if user is not None:
        login(request, user)
        return
    messages.error(request, 'invalid login details')
    return
    
    
def user_sign_out(request):
    logout(request)
    return ""


class UserProfile(DetailView):
    model = User


def user_edit_details(request, pk):
    user = User.objects.get(id=pk)
    form = CustomUserForm(instance=user)
    
    if request.method == "POST":
        form = CustomUserForm(request.POST, request.FILES, instance=user)
        
        if form.is_valid():
            form.save()
            
            return
        messages.error(request, f"Invalid entry")
        
    elif request.method == "GET":
        context = {
            "form": form
        }
        return
    
    
def change_password(request, pk):
    form = PasswordChangeForm(request.user)
    
    if request.method == "POST":
        form = PasswordChangeForm(request.user, request.POST)
        
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            
            return
        messages.error(request, "Please check your Input")
        
    context = {
        "form": form,
    }
    return