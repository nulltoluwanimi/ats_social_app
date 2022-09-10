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
    if request.user.username in event.yes:
        messages.error(request, "You have already accepted the invite")
        return HttpResponseRedirect(request.META.get("HTTP_REFERER"))
    event.yes.add(User.objects.get(id=pk))
    event.save()
    return HttpResponseRedirect(request.META.get("HTTP_REFERER"))


@login_required(login_url="accounts:sign_in")
def reject_invite(request, pk, id, _id):
    event = Event.running_objects.get(id=_id)
    if request.user.username in event.no:
        messages.error(request, "You have already rejected the invite")
        return HttpResponseRedirect(request.META.get("HTTP_REFERER"))
    event.no.add(User.objects.get(id=pk))
    event.save()
    return HttpResponseRedirect(request.META.get("HTTP_REFERER"))


@login_required(login_url="accounts:sign_in")
def inconclusive_decision_invite(request, pk, id, _id):
    event = Event.running_objects.get(id=_id)
    if request.user.username in event.maybe:
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
                # poll_option = poll_option["poll_1"] = [],
                # poll_option = poll_option["poll_2"] = [],
                # poll_option = poll_option["poll_3"] = [],
                # poll_option = poll_option["poll_4"] = [],
            )

            new_poll.save()

            messages.success(request, "Polls created successfully !")
            return HttpResponseRedirect(request.META.get("HTTP_REFERER"))

    context = {

    }
    return


def poll_option_1(request, pk, id, _id):
    poll = Poll.objects.get(id=_id)
    if pk not in poll.polls_option["poll_1"] and pk not in poll.polls_option["poll_2"] and pk not in poll.polls_option[
        "poll_3"] and pk not in poll.polls_option["poll_4"]:
        poll.polls_option["poll_1"].append(pk)
        poll.save()
        messages.success(request, "Vote recorded successfully")
        return HttpResponseRedirect(request.META.get("HTTP_REFERER"))
    messages.error(request, "You have voted before")
    return HttpResponseRedirect(request.META.get("HTTP_REFERER"))


def poll_option_2(request, pk, id, _id):
    poll = Poll.objects.get(id=_id)
    if pk not in poll.polls_option["poll_1"] and pk not in poll.polls_option["poll_2"] and pk not in poll.polls_option[
        "poll_3"] and pk not in poll.polls_option["poll_4"]:
        poll.polls_option["poll_2"].append(pk)
        poll.save()
        messages.success(request, "Vote recorded successfully")
        return HttpResponseRedirect(request.META.get("HTTP_REFERER"))
    messages.error(request, "You have voted before")
    return HttpResponseRedirect(request.META.get("HTTP_REFERER"))


def poll_option_3(request, pk, id, _id):
    poll = Poll.objects.get(id=_id)
    if pk not in poll.polls_option["poll_1"] and pk not in poll.polls_option["poll_2"] and pk not in poll.polls_option[
        "poll_3"] and pk not in poll.polls_option["poll_4"]:
        poll.polls_option["poll_3"].append(pk)
        poll.save()
        messages.success(request, "Vote recorded successfully")
        return HttpResponseRedirect(request.META.get("HTTP_REFERER"))
    messages.error(request, "You have voted before")
    return HttpResponseRedirect(request.META.get("HTTP_REFERER"))


def poll_option_4(request, pk, id, _id):
    poll = Poll.objects.get(id=_id)
    if pk not in poll.polls_option["poll_1"] and pk not in poll.polls_option["poll_2"] and pk not in poll.polls_option[
        "poll_3"] and pk not in poll.polls_option["poll_4"]:
        poll.polls_option["poll_4"].append(pk)
        poll.save()
        messages.success(request, "Vote recorded successfully")
        return HttpResponseRedirect(request.META.get("HTTP_REFERER"))
    messages.error(request, "You have voted before")
    return HttpResponseRedirect(request.META.get("HTTP_REFERER"))
