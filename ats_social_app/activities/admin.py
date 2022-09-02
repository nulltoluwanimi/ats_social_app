from multiprocessing import Event
from django.contrib import admin
from .models import Notification, Events, Polls
# Register your models here.
admin.site.register(Notification)
admin.site.register(Events)
admin.site.register(Polls)
