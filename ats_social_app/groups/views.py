from turtle import pos
from django.shortcuts import render, reverse
from django.contrib import messages
from django.db.models import Q
from django.http import HttpResponseRedirect, HttpResponseForbidden
from django.contrib.auth.decorators import login_required


from accounts.models import User
from .models import Comments, Group, Posts, Members, Likes, Replies, GroupRequest
from .forms import GroupCreateForm, PostForm, ReplyForm
from activities.models import Notification
# Create your views here.

def home(request): 
    search = request.GET.get("search") if request.GET.get(
        "search") is not None else ""

    list_of_groups = Group.active_objects.filter(Q(title__icontains=search) | Q(description__icontains=search)
                                                  | Q(owner_first_name__icontains=search) | Q(owner_last_name__icontains=search)
                                                  )
    
    context = {
        "list_of_groups": list_of_groups
    }
    return render(request,"", context)

    
@login_required(login_url="accounts:sign_in")
def group_details(request, pk, id):
    group = Group.objects.get(pk=id)
    member = Members.active_objects.get(user_id=pk, group_id=id)
    posts = Posts.objects.filter(group=group)
    
    if member is not None:
        if member.is_suspended :
            post_form = "You are not allowed to post"
            
        else:
            post_form = PostForm()
    
    if request.method == 'GET':
        context = {
            "group": group,
            "posts": posts,
            "form":post_form
        }
        
        return render(request, "", context)
    
    post_form = PostForm(request.POST)  
    
    if post_form.is_valid():
        post = post_form.save(commit=False)
        post.member = member
        post.group = group
        post.save()
        
        return HttpResponseRedirect(reverse())
        

def create_group(request, pk):
    form = GroupCreateForm()

    if request.method == "POST":
        form = GroupCreateForm(request.POST, request.FILES)

        if form.is_valid():
            # creator = form.save(commit=False)
            # creator.owner = User.objects.get(id=pk)

            # creator.save()
            new_group = Group.objects.create(owner=request.user, name_of_group=form.cleaned_data['name_of_group'],
                               title=form.cleaned_data['title'], description=form.cleaned_data['description'])
            new_group.save()
            print(new_group.id)
            group_admin = Members.objects.create(
                group=Group.objects.get(pk=new_group.id),  # STILL CHECK LATER
                member=request.user,
                is_admin=True,
            )

            group_admin.save()
            return HttpResponseRedirect(reverse('accounts:home'))
        error = (form .errors.as_text()).split('*')
        messages.error(request, error[len(error)-1])
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
    context = {
        'form': form,
    }
    return render(request, 'groups/create_group.html', context)


def make_admin(request, pk, id, _id):
    member = Members.objects.get(user_id=pk, group_id=id)
    
    if member.is_admin:
        pass
    else:
        return HttpResponseForbidden()
    
    group = Group.objects.get(id=pk)

    if len(group.members_set.all().filter(is_admin=True)) <= 3:
        member = Members.objects.get(
            Q(user_id=User.objects.get(id=_id).id) & Q(group=group))
        member.is_admin = True
        member.save()
        return HttpResponseRedirect(request.META.get("HTTP_REFERER"))
    messages.error(request, "Admin can not be more than 3")
    return HttpResponseRedirect(request.META.get("HTTP_REFERER"))


def remove_as_admin(request, pk, id, _id):
    group = Group.objects.get(id=pk)
    member = Members.objects.get(user_id=pk, group_id=id)
    
    if member.is_admin:
        pass
    else:
        return HttpResponseForbidden()

    if len(group.members_set.all().filter(is_admin=True)) > 1:
        member = Members.objects.get(
            Q(user_id=User.objects.get(id=id).id) & Q(group=group))
        member.is_admin = False
        member.save()
        return HttpResponseRedirect(request.META.get("HTTP_REFERER"))
    messages.error(request, "Admin can not be less than 1")
    return HttpResponseRedirect(request.META.get("HTTP_REFERER"))


def remove_member_of_group(request, pk, id, _id):
    group = Group.objects.get(id=pk)
    member = Members.objects.get(user_id=pk, group_id=id)
    
    if member.is_admin:
        pass
    else:
        return HttpResponseForbidden()
    member = Members.objects.get(
        Q(user_id=User.objects.get(id=_id).id) & Q(group=group))
    member.is_active = False
    member.save()
    return HttpResponseRedirect(request.META.get("HTTP_REFERER"))


def suspend_member(request, pk, id, _id):
    group = Group.objects.get(id=pk)
    member = Members.objects.get(user_id=pk, group_id=id)
    
    if member.is_admin:
        pass
    else:
        return HttpResponseForbidden()
    
    member = Members.objects.get(
        Q(user_id=User.objects.get(id=_id).id) & Q(group=group))
    member.is_suspended = True
    member.save()
    return HttpResponseRedirect(request.META.get("HTTP_REFERER"))


def join_group(request, pk, id):
    new_member = User.objects.get(id=pk)
    group = Group.objects.get(id=id)

    if group.is_closed:
        request = GroupRequest.objects.create(
            user=new_member,
            group=group,
            request_message=f"{new_member.username} wants to join {group.title}"
        )

        request.save()
        messages.success(
            request, "A request has been sent to the Admin of the group")
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
    return HttpResponseRedirect(reverse("groups:home"))


def create_reply(request, pk, id, _id):
    form = ReplyForm()
    
    if request.method == "POST":
        form = ReplyForm(request.POST)
        
        if form.is_valid():
            new_reply = form.save(commit=False)
            new_reply.user = User.objects.get(id=pk)
            new_reply.comment = Comments.active_objects.get(id=_id)
            new_reply.save()
            
            return
    
    
    context = {
        "form":form
    }
    return


def like_post(request, pk, id, _id):
    post_like = Likes.active_objects.get(member_id=pk, post_id=_id)
    
    if post_like is not None:
        post_like.is_active = False
        post_like.save()
        return HttpResponseRedirect(request.META.get("HTTP_REFERER"))
        
    else:
          post_like = Likes.objects.create(
              member = Members.active_objects.get(id=pk),
              post = Comments.active_objects.get(id=_id) 
          ) 
          post_like.save()
          return HttpResponseRedirect(request.META.get("HTTP_REFERER")) 
        
    

def like_comment(request, pk, id, _id):
    comment_like = Likes.active_objects.get(member_id=pk, comment_id=_id)
    
    if comment_like is not None:
        comment_like.is_active = False
        comment_like.save()
        return HttpResponseRedirect(request.META.get("HTTP_REFERER"))
        
    else:
          comment_like = Likes.objects.create(
              member = Members.active_objects.get(id=pk),
              comment = Comments.active_objects.get(id=_id) 
          ) 
          comment_like.save()
          return HttpResponseRedirect(request.META.get("HTTP_REFERER")) 
      

def like_reply(request, pk, id, _id):
    reply_like = Likes.active_objects.get(member_id=pk, reply_id=_id)
    
    if reply_like is not None:
        reply_like.is_active = False
        reply_like.save()
        return HttpResponseRedirect(request.META.get("HTTP_REFERER"))
        
    else:
          reply_like = Likes.objects.create(
              member = Members.active_objects.get(id=pk),
              reply = Comments.active_objects.get(id=_id) 
          ) 
          reply_like.save()
          return HttpResponseRedirect(request.META.get("HTTP_REFERER")) 
        
    
def hide_post(request, pk, id, _id):
    member = Members.active_objects.get(user_id=pk, group_id=id)
    
    if member.is_admin:
        post = Posts.active_objects.get(id=_id)
        post.is_active = False
        post.save()
        return HttpResponseRedirect(request.META.get("HTTP_REFERER"))
    messages.info(request, "You are not allowed to do that")
    return HttpResponseRedirect(request.META.get("HTTP_REFERER"))


def hide_comment(request, pk, id, _id):
    member = Members.active_objects.get(user_id=pk, group_id=id)
    
    if member.is_admin:
        comment = Comments.active_objects.get(id=_id)
        comment.is_active = False
        comment.save()
        return HttpResponseRedirect(request.META.get("HTTP_REFERER"))
    messages.info(request, "You are not allowed to do that")
    return HttpResponseRedirect(request.META.get("HTTP_REFERER"))



def hide_reply(request, pk, id, _id):
    member = Members.active_objects.get(user_id=pk, group_id=id)
    
    if member.is_admin:
        reply = Replies.active_objects.get(id=_id)
        reply.is_active = False
        reply.save()
        return HttpResponseRedirect(request.META.get("HTTP_REFERER"))
    messages.info(request, "You are not allowed to do that")
    return HttpResponseRedirect(request.META.get("HTTP_REFERER"))