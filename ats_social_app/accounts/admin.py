from django.contrib import admin

# Register your models here.
from .models import Post, Comments


class PostAdmin(admin.ModelAdmin):
    model = Post
    fields = ('title', 'image', 'tags','author','likes')

class CommentAdmin(admin.ModelAdmin):
    model = Comments
    fields = ('comment','post','user')


admin.site.register(Post, PostAdmin)
admin.site.register(Comments, CommentAdmin)

