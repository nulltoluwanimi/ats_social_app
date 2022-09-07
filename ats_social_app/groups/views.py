from turtle import pos
from django.shortcuts import render, reverse
from django.contrib import messages
from django.db.models import Q
from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import login_required

from accounts.models import User
from .models import Groups, Posts, Members, Likes, Replies, GroupRequest
from .forms import GroupCreateForm, PostForm
from activities.models import Notification


# Create your views here.


@login_required(login_url="accounts:sign_in")
def group_details(request, pk, type):
    if request.method == 'GET':
        try:
            group = Groups.objects.get(pk=pk)
            posts = Posts.objects.filter(group=group)
            return render(request, 'groups/group_edit.html', {"group": group,
                                                              "form": PostForm(),
                                                              "posts": posts})
        except Groups.DoesNotExist:
            return render(request, 'home.html')

    elif request.method == "POST":
        try:

            post_form = PostForm(request.POST)
            print(post_form.is_valid())

            if post_form.is_valid():
                new_post = post_form.save(commit=False)
                new_post.group = Groups.objects.get(pk=pk)
                new_post.save()
            else:
                error = (post_form.errors.as_text()).split("*")
                messages.error(request, error[len(error) - 1])

            return HttpResponseRedirect(reverse("groups:group", args=[pk, type]))
        except Groups.DoesNotExist:
            return render(request, 'home.html')


def create_group(request, pk):
    form = GroupCreateForm()

    if request.method == "POST":
        form = GroupCreateForm(request.POST, request.FILES)

        if form.is_valid():
            new_group = Groups(owner=request.user, name_of_group=form.cleaned_data['name_of_group'],
                               title=form.cleaned_data['title'], description=form.cleaned_data['description'])
            new_group.save()
            print(new_group.id)
            group_admin = Members.objects.create(
                group=Groups.objects.get(pk=new_group.id),  # STILL CHECK LATER
                member=request.user,

            )

            group_admin.save()
            return HttpResponseRedirect(reverse('accounts:home'))
        error = (form.errors.as_text()).split('*')
        messages.error(request, error[len(error) - 1])
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
    context = {
        'form': form,
    }
    return render(request, 'groups/create_group.html', context)


def make_admin(request, pk, id):
    group = Groups.objects.get(id=pk)

    if len(group.members_set.all().filter(is_admin=True)) <= 3:
        member = Members.objects.get(
            Q(user_id=User.objects.get(id=id).id) & Q(group=group))
        member.is_admin = True
        member.save()
        return HttpResponseRedirect(request.META.get("HTTP_REFERER"))
    messages.error(request, "Admin can not be more than 3")
    return HttpResponseRedirect(request.META.get("HTTP_REFERER"))


def remove_as_admin(request, pk, id):
    group = Groups.objects.get(id=pk)

    if len(group.members_set.all().filter(is_admin=True)) > 1:
        member = Members.objects.get(
            Q(user_id=User.objects.get(id=id).id) & Q(group=group))
        member.is_admin = False
        member.save()
        return HttpResponseRedirect(request.META.get("HTTP_REFERER"))
    messages.error(request, "Admin can not be less than 1")
    return HttpResponseRedirect(request.META.get("HTTP_REFERER"))


def remove_member_of_group(request, pk, id):
    group = Groups.objects.get(id=pk)
    member = Members.objects.get(
        Q(user_id=User.objects.get(id=id).id) & Q(group=group))
    member.is_active = False
    member.save()
    return HttpResponseRedirect(request.META.get("HTTP_REFERER"))


def suspend_member(request, pk, id):
    group = Groups.objects.get(id=pk)
    member = Members.objects.get(
        Q(user_id=User.objects.get(id=id).id) & Q(group=group))
    member.is_suspended = True
    member.save()
    return HttpResponseRedirect(request.META.get("HTTP_REFERER"))


def join_group(request, pk, id):
    new_member = User.objects.get(id=pk)
    group = Groups.objects.get(id=id)

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


def accept_request_closed_group(request, pk, id):
    specific_request = GroupRequest.objects.get(id=id)

    new_member = Members.objects.create(
        group=Groups.active_objects.get(group_id=specific_request.group_id),
        member=User.objects.get(id=specific_request.user_id)
    )
    new_member.save()

    return HttpResponseRedirect(reverse(request.META.get("HTTP_REFERER")))


def reject_request_closed_group(request, pk, id):
    specific_request = GroupRequest.objects.get(id=id)

    notification = Notification.objects.create(
        user=User.objects.get(id=specific_request.user_id),
        group=Groups.active_objects.get(id=specific_request.group_id),
        content=f"Your Request to join '{specific_request.group}' has been rejected, Sorry!"
    )

    notification.save()

    return HttpResponseRedirect(reverse(request.META.get("HTTP_REFERER")))


def exit_group(request, pk, id):
    member = Members.active_objects.get(user_id=pk, group_id=id)
    member.is_active = False
    member.save()
    return


def list_of_groups(request):
    search = request.GET.get("search") if request.GET.get(
        "search") is not None else ""

    list_of_groups = Groups.active_objects.filter(Q(title__icontains=search) | Q(description__icontains=search)
                                                  | Q(owner_first_name__icontains=search) | Q(
        owner_last_name__icontains=search)
                                                  )

    context = {
        "list_of_groups": list_of_groups,
    }

    return
