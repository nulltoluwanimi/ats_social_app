
from multiprocessing import context
from django.shortcuts import render
from django.contrib import messages
from django.views.generic import ListView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseRedirect 

from .forms import EventCreateForm, PollForms
from .models import Events, Notification, Polls
from accounts.models import User
from groups.models import Groups

# Create your views here.

#pk - user.id
#id = group.id
#_id = **kwargs

def create_event(request, pk, id):
    form = EventCreateForm()
    
    # implement something that converts is_started to true , using django datetime
    if request.method == "POST":
        form = EventCreateForm(request.POST, request.FILES)
        
        if form.is_valid():
            event = form.save(commit=False)
            event.creator = User.objects.get(id=pk)
            event.group = Groups.objects.get(id=id)
            event.save()
            
            notification =  Notification.objects.create(
                user=User.objects.get(id=pk),
                group= Groups.objects.get(id=id),
                content=request.POST["title"]
            
                
            )
            notification.save()
            
            messages.success(request, "Event Created Successfuly")
            return
        error = (form.errors.as_text()).split("*")
        messages.error(request, error[len(error) - 1])

    
    context = {
        "form": form
    }
    return


def edit_event(request, pk, id):
    event = Events.running_objects.get(id=id)
    form = EventCreateForm(instance=event)
    
    if request.method == "POST":
        form = EventCreateForm( request.POST, request.FILES, instance=event)
        
        if form.is_valid():
            form.save()
            
            return
        error = (form.errors.as_text()).split("*")
        messages.error(request, error[len(error) - 1])
    
    context = {
        "form": form,
    }
    return

class EventList(LoginRequiredMixin, ListView):
    model = Events
    template_name = ""
    context_object_name = "event_list"
    login_url = ""
    
    def get_queryset(self, **kwargs):
        return Events.running_objects.filter(group_id=kwargs["id"])


def accept_invite(request, pk, id, _id):
    event = Events.running_objects.get(id=_id)
    event.yes.append(User.objects.get(id=pk))
    event.save()
    return HttpResponseRedirect(request.META.get("HTTP_REFERER"))


def reject_invite(request, pk, id, _id):
    event = Events.running_objects.get(id=_id)
    event.no.append(User.objects.get(id=pk))
    event.save()
    return HttpResponseRedirect(request.META.get("HTTP_REFERER"))


def inconclusive_decision_invite(request, pk, id, _id):
    event = Events.running_objects.get(id=_id)
    event.maybe.append(User.objects.get(id=pk))
    event.save()
    return HttpResponseRedirect(request.META.get("HTTP_REFERER"))


class AdminEventDetail(DetailView):
    model = Events
    template_name = ""
    context = 'events'

    
    def get_queryset(self, **kwargs):
        return Events.objects.get(id=kwargs["_id"])



class AdminAllGroupEvents(ListView):
    model = Events
    template_name = ""
    context = "events"
    
    def get_queryset(self, **kwargs):
        return Events.objects.filter(group_id=kwargs["id"])


def create_polls(request, pk, id):
    form = PollForms()
    
    if request.method == "POST":
        form = PollForms(request.POST)
        
        if form.is_valid():
           new_poll =  Polls.objects.create(
                creator=User.objects.get(id=pk),
                group=Groups.objects.get(id=id),
                title=form.cleaned_data.get("title"),
                start_date=form.cleaned_data.get("start_date"),
                stop_date=form.cleaned_data.get("stop_date"),
                polls_option=polls_option[form.cleaned_data["polls_option1"]]=0,
                polls_option=polls_option[form.cleaned_data["polls_option2"]]=0,
                polls_option=polls_option[form.cleaned_data["polls_option3"]]=0,
                polls_option=polls_option[form.cleaned_data["polls_option4"]]=0,
            )
           new_poll.save()
           
           messages.success(request, "Polls created successfully !")
           return HttpResponseRedirect(request.META.get("HTTP_REFERER"))
    
    context = {
        
    }
    return


def polls_option1(request,pk, id, _id):
    poll = Polls.objects.get(id=_id)
    poll.polls_option["polls_1"] += 1
    poll.save()
    return HttpResponseRedirect(request.META.get("HTTP_REFERER"))


def polls_option2(request,pk, id, _id):
    poll = Polls.objects.get(id=_id)
    poll.polls_option["polls_2"] += 1
    poll.save()
    return HttpResponseRedirect(request.META.get("HTTP_REFERER"))

def polls_option2(request,pk, id, _id):
    poll = Polls.objects.get(id=_id)
    poll.polls_option["polls_3"] += 1
    poll.save()
    return HttpResponseRedirect(request.META.get("HTTP_REFERER"))

def polls_option2(request, id, _id):
    poll = Polls.objects.get(id=_id)
    poll.polls_option["polls_4"] += 1
    poll.save()
    return HttpResponseRedirect(request.META.get("HTTP_REFERER"))


