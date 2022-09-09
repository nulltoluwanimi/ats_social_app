import pycountry

from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate, update_session_auth_hash
from django.contrib import messages
from django.views.generic import DetailView, View, ListView
from django.contrib.auth.forms import PasswordChangeForm
from django.http import HttpResponseRedirect
from django.urls import reverse, reverse_lazy
from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.contrib.sites.shortcuts import get_current_site

from .forms import CustomUserForm, UserEditForm
from groups.models import Members, Posts, Comments, Replies, Group, GroupRequest
from activities.models import Notification

User = get_user_model()
countries = list(pycountry.countries)


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
            messages.error(request, error[len(error) - 1])
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


class UserProfile(ListView):
    model = User
    template_name = 'accounts/profile_view.html'

    def get_queryset(self, **kwargs):
        return User.objects.filter(id=self.kwargs["pk"]).first()

    def get_context_data(self, **kwargs):
        post_created = []
        comment_created = []
        replies_created = []
        group_requests = []
        user_notifications = User.objects.get(id=self.kwargs["pk"]).notification_users.all()
        number_of_groups = Members.active_objects.filter(member_id=self.kwargs["pk"])
        for member in number_of_groups:
            for post in Posts.objects.all():
                if member.id == post.member_id:
                    post_created.append(post)

        for member in number_of_groups:
            for comment in Comments.active_objects.all():
                if member.id == comment.member_id:
                    comment_created.append(comment)

        for member in number_of_groups:
            for reply in Replies.active_objects.all():
                if member.id == reply.member_id:
                    replies_created.append(reply)

        admin_for_request = Group.active_objects.filter(owner_id=self.kwargs["pk"])

        if admin_for_request is not None:
            a_creator = True

        for group in admin_for_request:
            for request in GroupRequest.active_objects.all():
                if group.id == request.group_id:
                    group_requests.append(request)

        context = super(UserProfile, self).get_context_data()
        context["user"] = self.get_queryset()
        context["groups"] = number_of_groups
        context["posts"] = post_created
        context["replies"] = replies_created
        context["notifications"] = user_notifications
        context["a_creator"] = a_creator
        context["requests"] = group_requests
        return context


def user_edit_details(request, pk):
    user = User.objects.get(id=pk)
    form = UserEditForm(instance=user)

    if request.method == "POST":
        form = UserEditForm(request.POST, request.FILES, instance=user)

        if form.is_valid():
            form.save()
            messages.success(request, "Edit successfully")

        error = (form.errors.as_text()).split('*')
        messages.error(request, error[len(error) - 1])
        return HttpResponseRedirect(reverse('accounts:profile', args=(pk,)))



    elif request.method == "GET":
        context = {
            "form": form,
            'countries': [country.name for country in countries]
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
