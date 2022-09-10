from django.contrib import admin
from .models import Group, GroupRequest,  Members, Posts, Comments, Replies, Likes
# Register your models here.
admin.site.register(Group)
admin.site.register(Members)
admin.site.register(Comments)
admin.site.register(Replies)
admin.site.register(Posts)
# admin.site.register(GroupRequest)
admin.site.register(Likes)
