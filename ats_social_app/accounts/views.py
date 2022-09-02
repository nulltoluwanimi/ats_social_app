from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate, update_session_auth_hash
from django.contrib import messages
from django.views.generic import DetailView, View
from django.contrib.auth.forms import PasswordChangeForm
from django.http import HttpResponseRedirect
from django.urls import reverse, reverse_lazy
from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.contrib.sites.shortcuts import get_current_site

from .forms import CustomUserForm, UserEditForm
User = get_user_model()

# Create your views here.


def home(request):
    return render(request, 'home.html')


def sign_up(request):
    form = CustomUserForm
    page = "accounts/sign_up.html"

    if request.method == "POST":
        form = CustomUserForm(request.POST)
        print(form.errors)
        if form.is_valid():
            new_user = User.objects.create_user(
                email=form.cleaned_data['email'],
                password=form.cleaned_data['password1'],
                username=form.cleaned_data['username']
            )

            return render(request, 'accounts/sign_in.html')

        else:
            error = (form.errors.as_text()).split('*')
            messages.error(request, error[len(error)-1])
            return render(request, "accounts/sign_up.html", )

    context = {"form": form,
               "page": page
               }
    return render(request, "accounts/sign_up.html", context)


def user_sign_in(request):

    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")

        try:
            user = User.objects.get(email=email.lower())

        except User.DoesNotExist:
            messages.error(request, "Invalid Email or Password")
            return HttpResponseRedirect(request.META.get("HTTP_REFERER"))
        print(email, password)
        user = authenticate(email=email, password=password)
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse('accounts:home'))
        print(user)
        messages.error(request, 'invalid login details')
        return HttpResponseRedirect(reverse('accounts:sign_in'))
    return render(request, 'accounts/sign_in.html')


def user_sign_out(request):
    logout(request)
    return render(request, 'accounts/sign_in.html')


class UserProfile(DetailView):
    model = User
    context_object_name = 'user'
    template_name = 'accounts/profile_view.html'


def user_edit_details(request, pk):
    user = User.objects.get(id=pk)
    form = UserEditForm(instance=user)

    if request.method == "POST":
        form = UserEditForm(request.POST, request.FILES, instance=user)

        if form.is_valid():
            form.save()
            messages.success(request, "Edit successfully")
            return HttpResponseRedirect(reverse('accounts:profile', args=({'pk': pk})))
        messages.error(request, f"Invalid entry")
        return HttpResponseRedirect(request.META.get("HTTP_REFERER"))

    elif request.method == "GET":
        context = {
            "form": form
        }
        return render(request, 'accounts/edit_profile.html', context)


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


class RecoverPassword(View):
    def get(self, request, *args, **kwargs):
        return render(request, "accounts/reset_password.html")

    def post(self, request):
        try:
            email = self.request.POST.get('email')
            user = User.objects.get(email=email)
            current_site = get_current_site(self.request)
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            token = default_token_generator.make_token(user)
            email_body = {
                'token': token,
                'subject': "Recover Password Mail.",
                'messages': f'Hi, {user.username}. continue http://{current_site}/password-token/{uid}/{token} to change your password, Thanks',
                'recipients': email
            }
            # send_mail_func(email_body)
            print(email_body)
            messages.success(request, f'An email has been sent to {email}')
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

        except User.DoesNotExist:
            messages.info(
                self.request, 'Hmmm!, cant find user with the email provided')
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


class ResetPassword(View):
    def get(self, request, uid, token):
        return render(request, 'accounts/new_password.html', {'uid': uid, 'token': token})

    def post(self, request, uid, token):
        try:
            uid_decode = urlsafe_base64_decode(uid)
            user = User.objects.get(pk=uid_decode)
            if default_token_generator.check_token(user, token):
                password = request.POST["password"]
                confirm_password = request.POST["confirm_password"]

                if password == confirm_password:
                    user.set_password(password)
                    user.save()
                    messages.success(
                        self.request, "Password changed successfully, you can now login")
                    return redirect('accounts:sign_in')
                else:
                    messages.error(self.request, "Password does not match")
                    return render(request, 'accounts/new_password.html', {'uid': uid, 'token': token})
            else:
                messages.error(
                    self.request, "Token does not seems to be valid")
                return render(request, 'accounts/new_password.html', {'uid': uid, 'token': token})
        except Exception as e:
            messages.error(request, "Seems the link has expired!, try again")
            return redirect('accounts:login')
