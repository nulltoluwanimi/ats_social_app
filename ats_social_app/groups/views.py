from turtle import pos
from django.shortcuts import render, reverse
from django.contrib import messages
from django.db.models import Q
from django.http import HttpResponseRedirect, HttpResponseForbidden
from django.contrib.auth.decorators import login_required

from accounts.models import User
from .models import Comments, Group, Posts, Members, Likes, Replies, GroupRequest

from .forms import GroupCreateForm, PostForm, ReplyForm, CommentForm
from activities.models import Notification, Event, Poll, EventInvite


# from activities.forms import EventCreateForm, PollForms


# Create your views here.


def group_search(request):
    search = request.POST.get("search") if request.POST.get(
        "search") is not None else ""

    list_of_groups = Group.active_objects.filter(Q(title__icontains=search) | Q(description__icontains=search)
                                                 | Q(owner__full_name__icontains=search)
                                                 | Q(name_of_group__icontains=search)
                                                 )

    print(list_of_groups)

    context = {
        "list_of_groups": list_of_groups
    }
    return render(request, "group_search.html", context)


@login_required(login_url="accounts:sign_in")
def group_details(request, pk, id):

    group = Group.objects.get(pk=id)
    check_member = Members.not_suspended_objects.filter(
        member_id=pk, group_id=id).first()
    notifications = Notification.objects.filter(group_id=id)
    posts = Posts.objects.filter(group=group)
    group_events = Event.objects.filter(group_id=id)
    group_polls = Poll.objects.filter(group_id=id).order_by('start_date')
    list_of_members = Members.not_suspended_objects.filter(group_id=id)
    suspended_members = Members.suspended_objects.filter(group_id=id)
    group_admin = Members.objects.filter(is_admin=True)
    try:
        event_invite = EventInvite.active_objects.filter(
            member_id=check_member.id)
    except EventInvite.DoesNotExist:
        event_invite = []

    context = {
        "group": group,
        "posts": posts,
        "events": event_invite,
        "group_events": group_events,
        "group_polls": group_polls,
        "members": list_of_members,
        "no_of_members": list_of_members.count(),
        "notifications": notifications,
        "check_member": check_member,
        "suspended_members": suspended_members,
        "group_admin": group_admin,
        "likes": [likes.post_id for likes in check_member.likes_set.all() if likes.is_active],

    }

    return render(request, "groups/group_edit.html", context)


@login_required(login_url="accounts:sign_in")
def create_group(request, pk):
    form = GroupCreateForm()

    if request.method == "POST":
        form = GroupCreateForm(request.POST, request.FILES)

        if form.is_valid():
            new_group = Group(owner=User.objects.get(id=pk), name_of_group=form.cleaned_data['name_of_group'],
                              title=form.cleaned_data['title'], description=form.cleaned_data['description'],
                              is_closed=form.cleaned_data["is_closed"])

            new_group.save()
            print(new_group.id)
            group_admin = Members.objects.create(
                group=Group.objects.get(pk=new_group.id),  # STILL CHECK LATER
                member=User.objects.get(id=pk),
                is_admin=True,
            )

            group_admin.save()

            notification = Notification.objects.create(
                content=f"{new_group.title} group created by {new_group.owner.username}",
                title=f"New Group Created",
                group=new_group,

            )

            notification.user.add(User.objects.get(id=pk))

            notification.save()
            return HttpResponseRedirect(reverse('accounts:home'))
        error = (form.errors.as_text()).split('*')
        messages.error(request, error[len(error) - 1])
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
    context = {
        'form': form,
    }
    return render(request, 'groups/create_group.html', context)


@login_required(login_url="accounts:sign_in")
def make_admin(request, pk, id, _id):
    check_member = Members.objects.get(member_id=pk, group_id=id)
    if check_member.is_admin:
        pass
    else:
        return HttpResponseForbidden()

    group = Group.objects.get(id=id)

    if len(group.members_set.all().filter(is_admin=True)) <= 3:
        member = Members.objects.get(
            Q(member_id=_id) & Q(group_id=id))
        member.is_admin = True
        member.save()

        notification = Notification.objects.create(
            content=f"{group.title} group assigned {member.member.username} as a group administrator",
            title=f"New Admin Assigned",
            group=group,

        )

        notification.save()
        messages.success(
            request, f"{member.member.username} made admin successfully")

        return HttpResponseRedirect(request.META.get("HTTP_REFERER"))
    messages.error(request, "Admin can not be more than 3")
    return HttpResponseRedirect(request.META.get("HTTP_REFERER"))


@login_required(login_url="accounts:sign_in")
def remove_as_admin(request, pk, id, _id):
    group = Group.objects.get(id=id)
    check_member = Members.objects.get(member_id=pk, group_id=id)

    if check_member.is_admin:
        pass
    else:
        return HttpResponseForbidden()

    if len(group.members_set.all().filter(is_admin=True)) > 1:
        member = Members.objects.get(
            # <<<<<<< HEAD
            #             Q(user_id=User.objects.get(id=id).id) & Q(group=group))
            # =======
            Q(member_id=_id) & Q(group_id=id))

        member.is_admin = False
        member.save()

        notification = Notification.objects.create(
            content=f"{group.title} group removed {member.member.username} as a group administrator",
            title=f" Admin Removed",
            group=group,

        )
        notification.save()

        messages.success(
            request, f"{member.member.username} removed as admin successfully")
        return HttpResponseRedirect(request.META.get("HTTP_REFERER"))
    messages.error(request, "Admin can not be less than 1")
    return HttpResponseRedirect(request.META.get("HTTP_REFERER"))


@login_required(login_url="accounts:sign_in")
def remove_member_of_group(request, pk, id, _id):

    group = Group.objects.get(id=id)
    member = Members.objects.get(member_id=pk, group_id=id)

    if member.is_admin:
        pass
    else:
        return HttpResponseForbidden()
    member = Members.objects.get(
        Q(member_id=_id) & Q(group_id=id))
    member.is_active = False
    member.save()

    notification = Notification.objects.create(
        content=f"The admin removed {member.member.username}",
        title=f"Member removed",
        group=group)

    notification.save()

    messages.success(
        request, f"{member.member.username} removed from {group} successfully")
    return HttpResponseRedirect(request.META.get("HTTP_REFERER"))


@login_required(login_url="accounts:sign_in")
def suspend_member(request, pk, id, _id):
    group = Group.objects.get(id=id)
    member = Members.objects.get(member_id=pk, group_id=id)

    if member.is_admin:
        pass
    else:
        return HttpResponseForbidden()

    member = Members.objects.get(Q(member_id=_id) & Q(group=group))
    member.is_suspended = True
    member.save()

    notification = Notification.objects.create(
        content=f"You have been suspended from {group}",
        title=f"Suspension",

    )

    notification.user.add(member.member)

    notification.save()
    messages.success(
        request, f"{member.member.username} suspended successfully")
    return HttpResponseRedirect(request.META.get("HTTP_REFERER"))


@login_required(login_url="accounts:sign_in")
def unsuspend_member(request, pk, id, _id):

    group = Group.objects.get(id=id)
    member = Members.objects.get(member_id=pk, group_id=id)

    if member.is_admin:
        pass
    else:
        return HttpResponseForbidden()

    member = Members.objects.get(Q(member_id=_id) & Q(group_id=id))
    member.is_suspended = False
    member.save()

    notification = Notification.objects.create(
        content=f"Your suspension in {group} has been lifted",
        title=f"Suspension Lifted",

    )

    notification.user.add(member.member)

    notification.save()
    messages.success(
        request, f"{member.member.username} suspension lifted successfully")
    return HttpResponseRedirect(request.META.get("HTTP_REFERER"))


@login_required(login_url="accounts:sign_in")
def join_group(request, pk, id):
    new_member = User.objects.get(id=pk)
    group = Group.objects.get(id=id)

    if group.is_closed:
        for member in group.members_set.all():
            if member.member_id == pk:

                messages.info(
                    request, f"You are already a member of {group.name_of_group}")
                return HttpResponseRedirect(request.META.get("HTTP_REFERER"))

        try:
            checker_2 = GroupRequest.active_objects.filter(
                user_id=pk, group_id=group.id).first()
            if checker_2 is not None:
                messages.error(
                    request, "A group request has been sent to the owner of the group")
                return HttpResponseRedirect(request.META.get("HTTP_REFERER"))
        except:
            pass

        group_request = GroupRequest.objects.create(
            user=User.objects.get(id=pk),
            group=group,
            request_message=f"{new_member.username} wants to join {group.title}"
        )
        group_request.save()

        notification = Notification.objects.create(
            content=f"{new_member.username} wants to join {group.title}",
        )

        for members in group.members_set.filter(is_admin=True):
            notification.user.add(members.member)

        notification.save()

        messages.success(
            request, "A request has been sent to the Admin of the group")
        return HttpResponseRedirect(request.META.get("HTTP_REFERER"))

    else:

        for member in group.members_set.filter(is_active=True):
            if member.member_id == pk:
                messages.info(
                    request, f"You are already a member of {group.name_of_group}")
                return HttpResponseRedirect(reverse("groups:group", args=[pk, id]))

        member = Members.objects.create(
            member=new_member,
            group=group
        )
        member.save()
        messages.success(
            request, f"you have joined '{group.name_of_group}' successfully")
        notification = Notification.objects.create(
            group=group,
            title="New Member",
            content=f"{new_member.username} has joined the group",

        )
        notification.save()
        return HttpResponseRedirect(reverse("groups:group", args=[pk, id]))


@login_required(login_url="accounts:sign_in")
def accept_request_closed_group(request, pk, id):
    specific_request = GroupRequest.objects.get(id=id)

    new_member = Members.objects.create(
        group=Group.active_objects.get(id=specific_request.group_id),
        member=User.objects.get(id=specific_request.user_id)
    )
    new_member.save()

    specific_request.is_active = False
    specific_request.save()

    notification = Notification.objects.create(
        content=f"Your Request to join '{specific_request.group}' has been accepted",
        title=f"Group Request"
    )
    notification.user.add(User.objects.get(id=specific_request.user_id))
    notification.save()

    return HttpResponseRedirect(request.META.get("HTTP_REFERER"))


def reject_request_closed_group(request, pk, id):
    specific_request = GroupRequest.active_objects.get(id=id)

    specific_request.is_active = False
    specific_request.save()

    notification = Notification.objects.create(
        title=f"Rejected Group Request",
        content=f"Your Request to join '{specific_request.group}' has been rejected, Sorry!"
    )
    notification.user.add(User.objects.get(id=specific_request.user_id))

    notification.save()

    messages.success(request, "request, rejected successfully")
    return HttpResponseRedirect(request.META.get("HTTP_REFERER"))


def exit_group(request, pk, id):

    member = Members.active_objects.get(member_id=pk, group_id=id)
    member.is_active = False
    member.save()

    notification = Notification.objects.create(
        group_id=member.group_id,
        content=f"{member.member.username} left the {member.group}",
    )

    notification.save()
    return HttpResponseRedirect(reverse("groups:home"))


@login_required(login_url="accounts:sign_in")
def create_reply(request, pk, id, _id):
    user = Members.objects.filter(member_id=pk, group_id=id).first()
    if user.is_suspended:
        messages.error(
            request, "You can't perform that action, please message admin")
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
    form = ReplyForm()

    if request.method == "POST":
        form = ReplyForm(request.POST)
        print(1, form.is_valid())
        if form.is_valid():
            new_reply = form.save(commit=False)
            new_reply.member = user
            new_reply.comment = Comments.active_objects.get(id=_id)
            new_reply.save()

    return HttpResponseRedirect(request.META.get("HTTP_REFERER"))


@login_required(login_url="accounts:sign_in")
def create_comment(request, pk, id):
    print("Creating comment...")
    user = Members.objects.filter(member_id=pk, group_id=id).first()
    if user.is_suspended:
        messages.error(
            request, "You can't perform that action, please message admin")
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
    form = CommentForm()

    if request.method == "POST":
        form = CommentForm(request.POST)

        if form.is_valid():
            new_reply = form.save(commit=False)
            new_reply.member = user
            new_reply.post = Posts.objects.get(id=id)
            new_reply.save()

            return HttpResponseRedirect(request.META.get("HTTP_REFERER"))


def post_detail(request, pk):
    post = Posts.objects.get(id=pk)
    comments = Comments.objects.filter(post_id=pk).order_by('-date_created')
    if request.user.is_authenticated:
        liked_comments = Likes.objects.filter(
            Q(comment_id__in=comments) & Q(post_id=pk) & Q(member__member_id=request.user.id))
    # replies = Replies.objects.filter(Q)
    print(liked_comments)
    context = {
        "post": post,
        # 'photo':request.user.profile_picture.url
        "liked_comments": [likes.comment_id for likes in liked_comments if likes.is_active],
        "comments": comments


    }
    return render(request, 'groups/post_detail.html', context)


def list_of_groups(request):
    search = request.GET.get("search") if request.GET.get(
        "search") is not None else ""

    list_of_groups = Group.active_objects.filter(Q(title__icontains=search) | Q(description__icontains=search)
                                                 | Q(owner_first_name__icontains=search) | Q(
        owner_last_name__icontains=search))

    context = {
        "form": list_of_groups
    }
    return


@login_required(login_url="accounts:sign_in")
def like_post(request, pk, id, _id):

    user = Members.objects.filter(member_id=pk, group_id=id).first()

    if user.is_suspended:
        messages.error(
            request, "You can't perform that action, please message admin")
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

    try:
        post_like = Likes.objects.filter(
            member=Members.objects.filter(member_id=pk, group_id=id).first(), post_id=_id)[0]

    except Exception as e:
        print(e)
        post_like = Likes.objects.create(
            member=Members.objects.filter(member_id=pk, group_id=id).first(), post_id=_id)[0]

    post_like.is_active = not post_like.is_active
    print(post_like.member)
    post_like.save()

    if post_like.is_active:
        notification = Notification.objects.create(
            group=Group.active_objects.get(id=id),
            title=f"{post_like.post.title}",
            content=f"{post_like.member.member.username} liked the post '{post_like.post.title}' ",
        )
        notification.user.add(User.objects.get(id=post_like.member.member.id))
        notification.save()
    return HttpResponseRedirect(request.META.get("HTTP_REFERER"))


@ login_required(login_url="accounts:sign_in")
def like_comment(request, pk, id, _id):
    user = Members.objects.filter(member_id=pk, group_id=id).first()
    if user.is_suspended:
        messages.error(
            request, "You can't perform that action, please message admin")
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

    comment_like = Likes.objects.get_or_create(
        member=Members.objects.get(member_id=pk, group_id=id), comment_id=_id, post_id=Comments.objects.get(id=_id).post_id)[0]
    print(comment_like.post)
    comment_like.is_active = not comment_like.is_active
    comment_like.save()

    if comment_like.is_active:
        notification = Notification.objects.create(
            group=Group.active_objects.get(id=id),
            title=f"{comment_like.post.title}",
            content=f"{comment_like.member.member.username} liked a comment in '{comment_like.comment}'",
        )

        notification.user.add(User.objects.get(
            id=comment_like.member.member.id))
        notification.save()

    return HttpResponseRedirect(request.META.get("HTTP_REFERER"))


@ login_required(login_url="accounts:sign_in")
def like_reply(request, pk, id, _id):
    # <<<<<<< HEAD
    #     reply_like = Likes.objects.get_or_create(
    #         member__member_id=pk, reply_id=_id)[0]
    # =======
    reply_like = Likes.objects.get_or_create(
        member=Members.objects.get(member_id=pk, group_id=id), reply_id=_id)[0]

    reply_like.is_active = not reply_like.is_active
    reply_like.save()

    if reply_like.is_active:
        notification = Notification.objects.create(
            group=Group.active_objects.get(id=id),
            title=f"{reply_like.post.title}",
            content=f"{reply_like.member.member.username} liked a reply to a comment in'{reply_like.reply}'")

        notification.user.add(User.objects.get(id=reply_like.member.member.id))
        notification.save()

    return HttpResponseRedirect(request.META.get("HTTP_REFERER"))


@ login_required(login_url="accounts:sign_in")
def create_post(request, pk, id):
    form = PostForm()

    user = Members.objects.filter(member_id=pk, group_id=id).first()
    if user.is_suspended:
        messages.error(
            request, "You can't perform that action, please message admin")
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

    if request.method == "POST":
        form = PostForm(request.POST)

        if form.is_valid():
            new_post = Posts(member=Members.active_objects.get(member_id=pk, group_id=id),
                             group=Group.active_objects.get(id=id),
                             title=form.cleaned_data['title'],
                             body=form.cleaned_data['body'],
                             )
            new_post.save()

            notification = Notification.objects.create(
                group=new_post.group,
                content=f"{user.member.username} created a post group",
                title=f"New post in {new_post.group}",
            )

            for members in new_post.group.members_set.filter(is_active=True, is_suspended=False):
                notification.user.add(members.member)
            notification.save()
            return HttpResponseRedirect(reverse("groups:group", args=[pk, id]))
        error = (form.errors.as_text()).split('*')
        messages.error(request, error[len(error) - 1])
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
    context = {
        'form': form,
    }
    return render(request, 'groups/post_create.html', context)


@login_required(login_url="accounts:sign_in")
def hide_post(request, pk, id, _id):
    member = Members.active_objects.get(member__member_id=pk, group_id=id)

    if member.is_admin:
        post = Posts.active_objects.get(id=_id)
        post.is_active = False
        post.save()
        return HttpResponseRedirect(request.META.get("HTTP_REFERER"))
    messages.info(request, "You are not allowed to do that")
    return HttpResponseRedirect(request.META.get("HTTP_REFERER"))


@login_required(login_url="accounts:sign_in")
def hide_comment(request, pk, id, _id):
    member = Members.active_objects.get(member__member_id=pk, group_id=id)

    if member.is_admin:
        comment = Comments.active_objects.get(id=_id)
        comment.is_active = False
        comment.save()
        return HttpResponseRedirect(request.META.get("HTTP_REFERER"))
    messages.info(request, "You are not allowed to do that")
    return HttpResponseRedirect(request.META.get("HTTP_REFERER"))


@login_required(login_url="accounts:sign_in")
def hide_reply(request, pk, id, _id):
    member = Members.active_objects.get(member__member_id=pk, group_id=id)

    if member.is_admin:
        reply = Replies.active_objects.get(id=_id)
        reply.is_active = False
        reply.save()
        return HttpResponseRedirect(request.META.get("HTTP_REFERER"))
    messages.info(request, "You are not allowed to do that")
    return HttpResponseRedirect(request.META.get("HTTP_REFERER"))
