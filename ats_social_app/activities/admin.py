from multiprocessing import Event
from django.contrib import admin
from .models import Notification, Event, Poll
# Register your models here.
admin.site.register(Notification)
admin.site.register(Event)
admin.site.register(Poll)
