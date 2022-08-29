from curses.ascii import HT
from django.shortcuts import render
from django.contrib import messages
from django.db.models import Q
from django.http import HttpResponseRedirect


from accounts.models import User
from .models import Groups, Posts, Members, Likes, Replies, GroupRequest
from .forms import GroupCreateForm
# Create your views here.



def create_group(request, pk):
    form = GroupCreateForm() 
    
    if request.method == "POST":
        form = GroupCreateForm(request.POST, request.FILES)
        
        
        if form.is_valid():
            creator = form.save(commit=False)
            creator.owner = User.objects.get(id=pk)
            creator.save()
            
            Members.objects.create(
                group=creator.id, #STILL CHECK LATER
                member=User.objects.get(id=pk),
                is_admin=True,
            )
            return
        messages.error(request, " ")

    context = {
        "form": form,
    }
    return 


def make_admin(request, pk, id):
    group = Groups.objects.get(id=pk)
    
    if len(group.members_set.all().filter(is_admin=True)) <= 3:
        member = Members.objects.get(Q(user_id=User.objects.get(id=id).id) & Q(group=group))
        member.is_admin = True
        member.save()
        return HttpResponseRedirect(request.META.get("HTTP_REFERER"))
    messages.error(request, "Admin can not be more than 3")
    return HttpResponseRedirect(request.META.get("HTTP_REFERER"))


def remove_as_admin(request, pk, id):
    group = Groups.objects.get(id=pk)
    
    if len(group.members_set.all().filter(is_admin=True)) > 1:
        member = Members.objects.get(Q(user_id=User.objects.get(id=id).id) & Q(group=group))
        member.is_admin = False
        member.save()
        return HttpResponseRedirect(request.META.get("HTTP_REFERER"))
    messages.error(request, "Admin can not be less than 1")
    return HttpResponseRedirect(request.META.get("HTTP_REFERER"))


def remove_member_of_group(request, pk, id):
    group = Groups.objects.get(id=pk)
    member = Members.objects.get(Q(user_id=User.objects.get(id=id).id) & Q(group=group))
    member.is_active = False 
    member.save()
    return HttpResponseRedirect(request.META.get("HTTP_REFERER"))


def suspend_member(request, pk, id):
    group = Groups.objects.get(id=pk)
    member = Members.objects.get(Q(user_id=User.objects.get(id=id).id) & Q(group=group))
    member.is_suspended = True
    member.save()
    return HttpResponseRedirect(request.META.get("HTTP_REFERER"))


def join_group(request, pk, id):
    new_member = User.objects.get(id=pk)
    group = Groups.objects.get(id=id)
    
    if group.is_closed:
        request = GroupRequest.objects.create(
            user=new_member,
            group=group
            request_message=f"{new_member.username} wants to join '{group.title}'"
        )
        
        request.save()
        messages.success(request, "A request has been sent to the Admin of the group")
        return HttpResponseRedirect(request.META.get("HTTP_REFERER"))
        
    else:
        member = Members.objects.create(
            member=new_member,
            group=group
        )
        member.save()
        return HttpResponseRedirect(request.META.get("HTTP_REFERER"))


def exit_group(request, pk, id):    
    member = Members.active_objects.get(user_id=pk, group_id=id)
    member.is_active = False
    member.save()
    return


def list_of_groups(request):
    
    search = request.GET.get("search") if request.GET.get("search") is not None else ""
    
    list_of_groups = Groups.active_objects.filter(Q(title__icontains=search) | Q(description__icontains=search)
                                                  | Q(owner_first_name__icontains=search) | Q(owner_last_name__icontains=search) 
                                                  )
    
    context = {
        "list_of_groups": list_of_groups,
    }
    
    return 
