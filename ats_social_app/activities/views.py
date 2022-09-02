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

#pk - user.id
#id = group.id
#_id = **kwargs
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
            
            notification =  Notification.objects.create(
                user=event.group.members_set.filter(is_admin_notification=True),
                group= Group.objects.get(id=id),
                content=request.POST["title"]
            
                
            )
            notification.save()
            
            messages.success(request, "Event Created Successfuly")
            return
    
    context = {
        "form": form
    }
    return


@login_required(login_url="accounts:sign_in")
def edit_event(request, pk, id, _id):
    event = Event.running_objects.get(id=_id)
    form = EventCreateForm(instance=event)

    if request.method == "POST":
        form = EventCreateForm( request.POST, request.FILES, instance=event)
        
        if form.is_valid():
            form.save()

            
            
            return
    
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
    event.yes.append(User.objects.get(id=pk))
    event.save()
    return HttpResponseRedirect(request.META.get("HTTP_REFERER"))


@login_required(login_url="accounts:sign_in")
def reject_invite(request, pk, id, _id):
    event = Event.running_objects.get(id=_id)
    event.no.append(User.objects.get(id=pk))
    event.save()
    return HttpResponseRedirect(request.META.get("HTTP_REFERER"))


@login_required(login_url="accounts:sign_in")
def inconclusive_decision_invite(request, pk, id, _id):
    event = Event.running_objects.get(id=_id)
    event.maybe.append(User.objects.get(id=pk))
    event.save()
    return HttpResponseRedirect(request.META.get("HTTP_REFERER"))


class AdminEventDetail(LoginRequiredMixin,UserPassesTestMixin,  DetailView):
    model = Event
    template_name = ""
    context = 'events'
    login_url = "accounts:sign_in"
    
    def test_func(self, **kwargs) :
        admin_status = Members.active_objects.get(user_id=kwargs["pk"], group_id=kwargs["id"])
        return admin_status.is_admin

    def get_queryset(self, **kwargs):
        return Event.objects.get(id=kwargs["_id"])



class AdminAllGroupEvents(LoginRequiredMixin,UserPassesTestMixin,  ListView):
    model = Event
    template_name = ""
    context = "events"
    login_url = "accounts:sign_in"
    
    def test_func(self, **kwargs) :
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
           new_poll =  Poll.objects.create(
                creator=User.objects.get(id=pk),
                group=Group.objects.get(id=id),
                title=form.cleaned_data.get("title"),
                start_date=form.cleaned_data.get("start_date"),
                stop_date=form.cleaned_data.get("stop_date"),
                
                #Tolu, There is an issue here , Kindly Check and Rectify
                polls_option=Poll.polls_option[form.cleaned_data["polls_option1"]]=0,
                polls_option=Poll.polls_option[form.cleaned_data["polls_option2"]]=0,
                polls_option=Poll.polls_option[form.cleaned_data["polls_option3"]]=0,
                polls_option=Poll.polls_option[form.cleaned_data["polls_option4"]]=0,
            )
           new_poll.save()
           
           messages.success(request, "Polls created successfully !")
           return HttpResponseRedirect(request.META.get("HTTP_REFERER"))
    
    context = {
        
    }
    return


@login_required(login_url="accounts:sign_in")
def polls_option1(request,pk, id, _id):
    poll = Poll.objects.get(id=_id)
    poll.polls_option["polls_1"] += 1
    poll.save()
    return HttpResponseRedirect(request.META.get("HTTP_REFERER"))


@login_required(login_url="accounts:sign_in")
def polls_option2(request,pk, id, _id):
    poll = Poll.objects.get(id=_id)
    poll.polls_option["polls_2"] += 1
    poll.save()
    return HttpResponseRedirect(request.META.get("HTTP_REFERER"))


@login_required(login_url="accounts:sign_in")
def polls_option3(request,pk, id, _id):
    poll = Poll.objects.get(id=_id)
    poll.polls_option["polls_3"] += 1
    poll.save()
    return HttpResponseRedirect(request.META.get("HTTP_REFERER"))


@login_required(login_url="accounts:sign_in")
def polls_option4(request, id, _id):
    poll = Poll.objects.get(id=_id)
    poll.polls_option["polls_4"] += 1
    poll.save()
    return HttpResponseRedirect(request.META.get("HTTP_REFERER"))


