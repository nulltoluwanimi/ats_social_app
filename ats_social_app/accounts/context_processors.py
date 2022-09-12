from groups.models import Group, GroupRequest, Members, Posts, Comments, Replies, Likes
from activities.models import Notification, Event, Poll
from accounts.models import User


def context(request):
    # print(request.user.is_authenticated)
    context = {}
    try:
        context['recently_created_groups'] = Group.objects.all().order_by(
            '-date_created')[:5]

        context['open_events'] = Event.objects.filter(
            group__is_closed=False)[:4]
        context['open_posts'] = Posts.objects.filter(
            group__is_closed=False)
        context['all_groups'] = Group.objects.all().order_by(
            '-date_created')[:10]
        if request.user.is_authenticated:
            all_user_group = Members.objects.filter(
                member_id=request.user.id, is_active=True).values_list('group_id')
            context['user_group'] = Group.objects.filter(pk__in=all_user_group)
            context["user_notifications"] = (User.objects.get(id=request.user.id)).notification_users.all()
            context['not_user_groups'] = Group.objects.exclude(pk__in=all_user_group)[
                :10]
        return context
    except Exception as e:
        print(e)
        return context
