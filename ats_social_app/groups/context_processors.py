from .models import Groups, GroupRequest,  Members, Posts, Comments, Replies, Likes


def context(request):
    context = {}
    context['recently_created_groups'] = Groups.objects.all().order_by(
        '-date_created')[:5]

    print(context)
    return context
