from groups.models import Group, GroupRequest,  Members, Posts, Comments, Replies, Likes
from activities.models import Notification, Event, Poll


def context(request):
    context = {}
    try:
        context['recently_created_groups'] = Group.objects.all().order_by(
            '-date_created')[:5]

        context['open_events'] = Event.objects.filter(
            group__is_closed=False).order_by('date_created')[:4]
        context['open_posts'] = Posts.objects.filter(
            group__is_closed=False).order_by('date_created')
        context['all_groups'] = Group.objects.all().order_by(
            '-date_created')[:10]
        # print(context)
        return context
    except Exception as e:
        return context
