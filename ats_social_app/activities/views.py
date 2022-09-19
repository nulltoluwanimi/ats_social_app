
from django.shortcuts import render, reverse
from django.contrib import messages
from django.views.generic import ListView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import UserPassesTestMixin, LoginRequiredMixin

from .forms import EventCreateForm, PollForms
from .models import Event, Notification, Poll, EventInvite
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

            for members in event.group.members_set.filter(is_admin=True, is_suspended=False):
                notification.user.add(members.member)
            notification.save()

            for all_members in event.group.members_set.filter(is_suspended=False):
                event_invite = EventInvite.objects.create(
                    member=all_members,
                    event=event

                )
                event_invite.save()

            messages.success(request, "Event Created Successfully")
            return HttpResponseRedirect(reverse("groups:group", args=[pk, id]))
        error = (form.errors.as_text()).split("*")
        messages.error(request, error[len(error) - 1])

    context = {
        "form": form
    }
    return render(request, "groups/create_event.html", context)


def calendar_event_view(request, pk, id):
    context = {
        "group_events": Event.objects.filter(group_id=id)
    }
    return render(request, "groups/event_calendar.html", context)


@login_required(login_url="accounts:sign_in")
def edit_event(request, pk, id, _id):
    event = Event.running_objects.get(id=_id)
    form = EventCreateForm(instance=event)

    if request.method == "POST":
        form = EventCreateForm(request.POST, request.FILES, instance=event)

        if form.is_valid():
            form.save()

            messages.success(request, "Event edited successfully")
            return HttpResponseRedirect(reverse("groups:group", args=[pk, id]))
        error = (form.errors.as_text()).split("*")
        messages.error(request, error[len(error) - 1])

    context = {
        "form": form,
    }
    return render(request, "groups/create_event.html", context)


class EventList(LoginRequiredMixin, ListView):
    model = Event
    template_name = ""
    context_object_name = "event_list"
    login_url = "accounts:sign_in"

    def get_queryset(self, **kwargs):
        return Event.running_objects.filter(group_id=kwargs["id"])


@login_required(login_url="accounts:sign_in")
def accept_invite(request, pk, id, _id, __id):
    event = Event.running_objects.get(id=_id)
    if request.user in event.yes:
        messages.error(request, "You have already accepted the invite")
        return HttpResponseRedirect(request.META.get("HTTP_REFERER"))
    event.yes.append(pk)
    event.save()
    event_invite = EventInvite.active_objects.get(id=__id)
    event_invite.is_active = False
    event_invite.save()
    messages.success(request, "Splendid , we will be expecting you")

    return HttpResponseRedirect(request.META.get("HTTP_REFERER"))


@login_required(login_url="accounts:sign_in")
def reject_invite(request, pk, id, _id, __id):
    event = Event.running_objects.get(id=_id)
    if request.user.username in event.no:
        messages.error(request, "You have already rejected the invite")
        return HttpResponseRedirect(request.META.get("HTTP_REFERER"))
    event.no.append(pk)
    event.save()
    event_invite = EventInvite.active_objects.get(id=__id)
    event_invite.is_active = False
    event_invite.save()
    messages.success(request, "We would have loved to see you but, OH WELL !")

    return HttpResponseRedirect(request.META.get("HTTP_REFERER"))


@login_required(login_url="accounts:sign_in")
def inconclusive_decision_invite(request, pk, id, _id, __id):
    event = Event.running_objects.get(id=_id)
    if request.user.username in event.maybe:
        messages.error(request, "You have already selected maybe")
        return HttpResponseRedirect(request.META.get("HTTP_REFERER"))
    event.maybe.append(pk)
    event.save()
    event_invite = EventInvite.active_objects.get(id=__id)
    event_invite.is_active = False
    event_invite.save()
    messages.success(request, "Ooops, oh well !")

    return HttpResponseRedirect(request.META.get("HTTP_REFERER"))


class AdminEventDetail(LoginRequiredMixin, UserPassesTestMixin, DetailView):
    model = Event
    template_name = ""
    context = 'events'
    login_url = "accounts:sign_in"

    def test_func(self, **kwargs):
        admin_status = Members.active_objects.get(
            user_id=kwargs["pk"], group_id=kwargs["id"])
        return admin_status.is_admin

    def get_queryset(self, **kwargs):
        return Event.objects.get(id=kwargs["_id"])


class AdminAllGroupEvents(LoginRequiredMixin, UserPassesTestMixin, ListView):
    model = Event
    template_name = ""
    context = "events"
    login_url = "accounts:sign_in"

    def test_func(self, **kwargs):
        admin_status = Members.active_objects.get(
            user_id=kwargs["pk"], group_id=kwargs["id"])
        return admin_status.is_admin

    def get_queryset(self, **kwargs):
        return Event.objects.filter(group_id=kwargs["id"])


@login_required(login_url="accounts:sign_in")
def create_polls(request, pk, id):
    print(request.POST)
    form = PollForms()

    if request.method == "POST":
        form = PollForms(request.POST)
        print(form.is_valid())
        if form.is_valid():

            polls = {
                f'{request.POST.get("poll_option1")}': [],
                f'{request.POST.get("poll_option2")}': [],
                f'{request.POST.get("poll_option3", "")}': [],
                f'{request.POST.get("poll_option4", "")}': [],
            }
            new_poll = Poll.objects.create(
                creator=User.objects.get(id=pk),
                group=Group.objects.get(id=id),
                title=form.cleaned_data.get("title"),
                start_date=form.cleaned_data.get("start_date"),
                stop_date=form.cleaned_data.get("stop_date"),
                poll_option=polls
            )

            new_poll.save()

            messages.success(request, "Polls created successfully !")

        error = (form .errors.as_text()).split('*')
        messages.error(request, error[len(error)-1])
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

    context = {
        "form": form,
        'group': id
    }

    return render(request, 'groups/create_polls.html', context)


def poll_option(request, pk,  id):
    try:
        option = request.POST['option']

        poll = Poll.objects.get(pk=id)

        poll__option = list(poll.poll_option.keys())

        print(poll__option, option)

        if len(poll__option) == 4:
            if pk not in poll.poll_option[f'{poll__option[0]}'] and pk not in poll.poll_option[f'{poll__option[1]}'] and pk not in poll.poll_option[f'{poll__option[2]}'] and pk not in poll.poll_option[f'{poll__option[3]}']:
                poll.poll_option[f"{option}"].append(pk)
                poll.save()
                messages.success(request, "Vote recorded successfully")
                return HttpResponseRedirect(request.META.get("HTTP_REFERER"))
            messages.info(request, "You have voted before")
            return HttpResponseRedirect(request.META.get("HTTP_REFERER"))

        if len(poll__option) == 3:
            if pk not in poll.poll_option[f'{poll__option[0]}'] and pk not in poll.poll_option[f'{poll__option[1]}'] and pk not in poll.poll_option[f'{poll__option[2]}']:
                poll.poll_option[f"{option}"].append(pk)
                poll.save()
                messages.success(request, "Vote recorded successfully")
                return HttpResponseRedirect(request.META.get("HTTP_REFERER"))
            messages.info(request, "You have voted before")
            return HttpResponseRedirect(request.META.get("HTTP_REFERER"))

        if len(poll__option) == 2:
            if pk not in poll.poll_option[f'{poll__option[0]}'] and pk not in poll.poll_option[f'{poll__option[1]}']:
                poll.poll_option[f"{option}"].append(pk)
                poll.save()
                messages.success(request, "Vote recorded successfully")
                return HttpResponseRedirect(request.META.get("HTTP_REFERER"))
            messages.info(request, "You have voted before")
            return HttpResponseRedirect(request.META.get("HTTP_REFERER"))
    except Poll.DoesNotExist:
        messages.error(request, "An error occurred")
        return HttpResponseRedirect(request.META.get("HTTP_REFERER"))


# def poll_option_2(request, pk, id, _id):
#     poll = Poll.objects.get(id=_id)
#     if pk not in poll.polls_option["poll_1"] and pk not in poll.polls_option["poll_2"] and pk not in poll.polls_option[
#             "poll_3"] and pk not in poll.polls_option["poll_4"]:
#         poll.polls_option["poll_2"].append(pk)
#         poll.save()
#         messages.success(request, "Vote recorded successfully")
#         return HttpResponseRedirect(request.META.get("HTTP_REFERER"))
#     messages.error(request, "You have voted before")
#     return HttpResponseRedirect(request.META.get("HTTP_REFERER"))


# def poll_option_3(request, pk, id, _id):
#     poll = Poll.objects.get(id=_id)
#     if pk not in poll.polls_option["poll_1"] and pk not in poll.polls_option["poll_2"] and pk not in poll.polls_option[
#             "poll_3"] and pk not in poll.polls_option["poll_4"]:
#         poll.polls_option["poll_3"].append(pk)
#         poll.save()
#         messages.success(request, "Vote recorded successfully")
#         return HttpResponseRedirect(request.META.get("HTTP_REFERER"))
#     messages.error(request, "You have voted before")
#     return HttpResponseRedirect(request.META.get("HTTP_REFERER"))


# def poll_option_4(request, pk, id, _id):
#     poll = Poll.objects.get(id=_id)
#     if pk not in poll.polls_option["poll_1"] and pk not in poll.polls_option["poll_2"] and pk not in poll.polls_option[
#             "poll_3"] and pk not in poll.polls_option["poll_4"]:
#         poll.polls_option["poll_4"].append(pk)
#         poll.save()
#         messages.success(request, "Vote recorded successfully")
#         return HttpResponseRedirect(request.META.get("HTTP_REFERER"))
#     messages.error(request, "You have voted before")
#     return HttpResponseRedirect(request.META.get("HTTP_REFERER"))
