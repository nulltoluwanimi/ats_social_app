from django.shortcuts import render
from django.contrib import messages
from django.views.generic import ListView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import UserPassesTestMixin, LoginRequiredMixin

from .forms import EventCreateForm, PollForms
from .models import Event, Notification, Poll
from accounts.models import User
from groups.models import Group, Members


# Create your views here.

# pk - user.id
# id = group.id
# _id = **kwargs
@login_required(login_url="accounts:sign_in")
def create_event(request, pk, id):
    form = EventCreateForm()

    # implement something that converts is_started to true , using django datetime
    if request.method == "POST":
        form = EventCreateForm(request.POST, request.FILES)

        if form.is_valid():
            event = form.save(commit=False)
            event.creator = User.objects.get(id=pk)
            event.group = Group.objects.get(id=id)
            event.save()

            notification = Notification.objects.create(
                title=f"{event.group}'s event creation",
                group=Group.objects.get(id=id),
                content=form.cleaned_data["title"],
                is_admin_notification=True

            )
            for members in event.group.members_set.filter(is_admin=True):
                notification.user.add(members.member)

            notification.save()

            messages.success(request, "Event Created Successfuly")
            return
        error = (form.errors.as_text()).split("*")
        messages.error(request, error[len(error) - 1])

    context = {
        "form": form
    }
    return


@login_required(login_url="accounts:sign_in")
def edit_event(request, pk, id, _id):
    event = Event.running_objects.get(id=_id)
    form = EventCreateForm(instance=event)

    if request.method == "POST":
        form = EventCreateForm(request.POST, request.FILES, instance=event)

        if form.is_valid():
            form.save()

            messages.success(request, "Event edited successfully")
            return
        error = (form.errors.as_text()).split("*")
        messages.error(request, error[len(error) - 1])

    context = {
        "form": form,
    }
    return


class EventList(LoginRequiredMixin, ListView):
    model = Event
    template_name = ""
    context_object_name = "event_list"
    login_url = "accounts:sign_in"

    def get_queryset(self, **kwargs):
        return Event.running_objects.filter(group_id=kwargs["id"])


@login_required(login_url="accounts:sign_in")
def accept_invite(request, pk, id, _id):
    event = Event.running_objects.get(id=_id)
    if request.user.username in event.yes.all():
        messages.error(request, "You have already accepted the invite")
        return HttpResponseRedirect(request.META.get("HTTP_REFERER"))
    event.yes.add(User.objects.get(id=pk))
    event.save()
    return HttpResponseRedirect(request.META.get("HTTP_REFERER"))


@login_required(login_url="accounts:sign_in")
def reject_invite(request, pk, id, _id):
    event = Event.running_objects.get(id=_id)
    if request.user.username in event.no.all():
        messages.error(request, "You have already rejected the invite")
        return HttpResponseRedirect(request.META.get("HTTP_REFERER"))
    event.no.add(User.objects.get(id=pk))
    event.save()
    return HttpResponseRedirect(request.META.get("HTTP_REFERER"))


@login_required(login_url="accounts:sign_in")
def inconclusive_decision_invite(request, pk, id, _id):
    event = Event.running_objects.get(id=_id)
    if request.user.username in event.yes.all():
        messages.error(request, "You have already selected maybe")
        return HttpResponseRedirect(request.META.get("HTTP_REFERER"))
    event.maybe.append(User.objects.get(id=pk))
    event.save()
    return HttpResponseRedirect(request.META.get("HTTP_REFERER"))


class AdminEventDetail(LoginRequiredMixin, UserPassesTestMixin, DetailView):
    model = Event
    template_name = ""
    context = 'events'
    login_url = "accounts:sign_in"

    def test_func(self, **kwargs):
        admin_status = Members.active_objects.get(user_id=kwargs["pk"], group_id=kwargs["id"])
        return admin_status.is_admin

    def get_queryset(self, **kwargs):
        return Event.objects.get(id=kwargs["_id"])


class AdminAllGroupEvents(LoginRequiredMixin, UserPassesTestMixin, ListView):
    model = Event
    template_name = ""
    context = "events"
    login_url = "accounts:sign_in"

    def test_func(self, **kwargs):
        admin_status = Members.active_objects.get(user_id=kwargs["pk"], group_id=kwargs["id"])
        return admin_status.is_admin

    def get_queryset(self, **kwargs):
        return Event.objects.filter(group_id=kwargs["id"])


@login_required(login_url="accounts:sign_in")
def create_polls(request, pk, id):
    form = PollForms()

    if request.method == "POST":
        form = PollForms(request.POST)

        if form.is_valid():
            new_poll = Poll.objects.create(
                creator=User.objects.get(id=pk),
                group=Group.objects.get(id=id),
                title=form.cleaned_data.get("title"),
                start_date=form.cleaned_data.get("start_date"),
                stop_date=form.cleaned_data.get("stop_date"),

                # Tolu, There is an issue here , Kindly Check and Rectify
                # polls_option=Poll.polls_option[form.cleaned_data["polls_option1"]]=0,
                # polls_option=Poll.polls_option[form.cleaned_data["polls_option2"]]=0,
                # polls_option=Poll.polls_option[form.cleaned_data["polls_option3"]]=0,
                # polls_option=Poll.polls_option[form.cleaned_data["polls_option4"]]=0,
            )
            new_poll.save()

            notification = Notification.objects.create(
                title=f"Poll created by{new_poll.creator.username}",
                group=Group.objects.get(id=id),
                content=f'{form.cleaned_data.get("title")}',

            )

            for members in new_poll.group.member_set.all():
                notification.user.add(members.member)
            notification.save()

            messages.success(request, "Polls created successfully !")
            return HttpResponseRedirect(request.META.get("HTTP_REFERER"))

    context = {

    }
    return render(request, "groups/create_polls.html", context)


@login_required(login_url="accounts:sign_in")
def polls_option1(request, pk, id, _id):
    poll = Poll.objects.get(id=_id)
    poll.polls_option_1.add(User.objects.get(id=pk))
    poll.save()
    return HttpResponseRedirect(request.META.get("HTTP_REFERER"))


@login_required(login_url="accounts:sign_in")
def polls_option2(request, pk, id, _id):
    poll = Poll.objects.get(id=_id)
    poll.polls_option_2.add(User.objects.get(id=pk))
    poll.save()
    return HttpResponseRedirect(request.META.get("HTTP_REFERER"))


@login_required(login_url="accounts:sign_in")
def polls_option3(request, pk, id, _id):
    poll = Poll.objects.get(id=_id)
    poll.polls_option_3.add(User.objects.get(id=pk))
    poll.save()
    return HttpResponseRedirect(request.META.get("HTTP_REFERER"))


@login_required(login_url="accounts:sign_in")
def polls_option4(request, id, _id):
    poll = Poll.objects.get(id=_id)
    poll.polls_option_4.add(User.objects.get(id=pk))
    poll.save()
    return HttpResponseRedirect(request.META.get("HTTP_REFERER"))
