from google.oauth2 import service_account
from googleapiclient.discovery import build
from django.contrib import messages

service_account_email = "beam-60@arcane-pipe-362414.iam.gserviceaccount.com"
SCOPES = ["https://www.googleapis.com/auth/calendar"]

service_account_file = 'helpers/service_account.json'

credentials = service_account.Credentials.from_service_account_file(service_account_file)
scoped_credentials = credentials.with_scopes(SCOPES)


def build_service():
    service = build("calendar", "v3", credentials=scoped_credentials)
    return service


def create_event_signal(request, **kwargs):
    service = build_service()

    start_datetime = kwargs["time_start"]
    end_datetime = kwargs["time_end"]
    event = (
        service.events()
        .insert(
            calendarId='6c67cjbr099g280mkub1ottibk@group.calendar.google.com',
            body={
                "summary": kwargs["title"],
                "description": kwargs["description"],
                "start": {"dateTime": start_datetime},
                "end": {
                    "dateTime": end_datetime
                },
            },
        )
        .execute()
    )

    return messages.success(request, "Event added to your calendar")
