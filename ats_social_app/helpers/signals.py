import os

from django.db.models.signals import post_delete, post_save
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from oauth2client.service_account import ServiceAccountCredentials

from activities.models import Event
from ..ats_social_app.settings import CAL_ID

# If modifying these scopes, delete the file token.json.
SCOPES = ["https://www.googleapis.com/auth/calendar"]


def get_service(refresh=False):
    # credentials = ServiceAccountCredentials.from_json_keyfile_dict(
    #     json.loads(os.environ.get("service-account")), scopes=SCOPES
    # )
    # # or if you have a file
    credentials = ServiceAccountCredentials.from_json_keyfile_name(
        filename="service-account.json", scopes=SCOPES
    )
    service = build("calendar", "v3", credentials=credentials)
    return service


def handle_event(sender, created, instance, **kwargs):
    """this function creates the events in the google agenda and updates them if changed in the website"""
    service = get_service()
    event = instance
    queryset = Event.objects.filter(
        id=event.id
    )  # https://stackoverflow.com/questions/1555060/how-to-save-a-model-without-sending-a-signal
    # this is used so that we can update the google event within this signal without reshooting this signal(signals
    # shot every time an object is saved)
    event = {
        "summary": event.description,
        "location": event.location,
        "description": (event.description + " " + event.summary),
        "start": {
            "dateTime":
                event.time_start
            ,
            "timeZone": "Lagos/Africa",
        },
        "end": {
            "dateTime":
                event.time_end
            ,
            "timeZone": "Lagos/Africa",
        },
        "recurrence": [],
        "reminders": {},
    }

    if created or not instance.google_link:
        try:
            event = (
                service.events()
                .insert(
                    calendarId=CAL_ID,
                    body=event,
                )
                .execute()
            )
            queryset.update(google_link=event["id"])
        except HttpError as error:
            # print("An error occurred: %s" % error)
            pass
    else:
        try:
            event = (
                service.events()
                .update(
                    calendarId=CAL_ID,
                    body=event,
                    eventId=instance.google_link,
                )
                .execute()
            )
            queryset.update(google_link=event["id"])
        except HttpError as error:
            # print("An error occurred: %s" % error)
            pass
    # print("#############ADDED NEW       #############")


def delete_event(sender, instance, **kwargs):
    """this function deletes an event from google agenda when deleted in the website"""
    try:
        service = get_service()
        service.events().delete(
            calendarId=CAL_ID,
            eventId=instance.google_link,
        ).execute()
    except:
        pass


post_save.connect(handle_event, sender=Event)
post_delete.connect(delete_event, sender=Event)
