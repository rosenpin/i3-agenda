
import os
import re
from typing import List
import datetime
import pickle

from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build, Resource

from event import Event
from event_utils import get_event_time, is_allday
from config import CONF_DIR, URL_REGEX

SCOPES = ["https://www.googleapis.com/auth/calendar.readonly"]
TMP_TOKEN = f"{CONF_DIR}/i3agenda_google_token.pickle"


def connect(credspath: str) -> Resource:
    creds = get_credentials(credspath)

    service = build("calendar", "v3", credentials=creds)
    return service


def get_credentials(credspath):
    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.

    if os.path.exists(TMP_TOKEN):
        with open(TMP_TOKEN, "rb") as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if not os.path.exists(credspath):
            print(
                '''You need to download your credentials json file from the 
                   Google API Console and pass its path to this script'''
            )
            exit(1)
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(credspath, SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open(TMP_TOKEN, "wb") as token:
            pickle.dump(creds, token)
    return creds


def get_callendar_ids(allowed_calendars_ids: List[str], service: Resource) -> List:
    calendar_ids = []
    while True:
        calendar_list = service.calendarList().list().execute()
        for calendar_list_entry in calendar_list["items"]:
            if (
                    not allowed_calendars_ids
                    or calendar_list_entry["id"] in allowed_calendars_ids
            ):
                calendar_ids.append(calendar_list_entry["id"])
        page_token = calendar_list.get("nextPageToken")
        if not page_token:
            break
    return calendar_ids


def event_from_json(event):
    end_time = get_event_time(event["end"].get("dateTime", event["end"].get("date")))
    start_time = event["start"].get("dateTime", event["start"].get("date"))
    unix_time = get_event_time(start_time)

    location = None

    if "location" in event:
        location = event["location"]
    elif "description" in event:
        matches = re.findall(URL_REGEX, event["description"])
        location = matches[0][0] if matches else None

    return Event(
            event["summary"],
            is_allday(start_time),
            unix_time,
            end_time,
            location,
        )


def get_event_result_today_only(service, calendar_id, max_results):
    now = datetime.datetime.utcnow()
    now_rfc3339 = now.isoformat() + "Z"  # 'Z' indicates UTC time
    midnight_rfc3339 = (
            now.replace(hour=23, minute=39, second=59).isoformat() + "Z"
    )
    return (service.events()
            .list(
                calendarId=calendar_id,
                timeMin=now_rfc3339,
                timeMax=midnight_rfc3339,
                maxResults=max_results,
                singleEvents=True,
                orderBy="startTime",
            )
            .execute())


def get_event_result(service, calendar_id, max_results):
    now = datetime.datetime.utcnow()
    now_rfc3339 = now.isoformat() + "Z"  # 'Z' indicates UTC time
    return (service.events()
            .list(
                calendarId=calendar_id,
                timeMin=now_rfc3339,
                maxResults=max_results,
                singleEvents=True,
                orderBy="startTime",
            )
            .execute())


def get_all_events(calendar_ids, service, max_results, today_only):
    all_events = []

    for calendar_id in calendar_ids:
        if today_only:
            events_result = get_event_result_today_only(service, calendar_id, max_results)
        else:
            events_result = get_event_result(service, calendar_id, max_results)
        events = events_result.get("items", [])

        if not events:
            continue

        for event in events:
            all_events.append(event_from_json(event))

    return all_events


def getEvents(
        credentials: str, allowed_calendars_ids: List[str], max_results: int, today_only=False
) -> List[Event]:
    service = connect(credentials)

    calendar_ids = get_callendar_ids(allowed_calendars_ids, service)

    all_events = get_all_events(calendar_ids, service, max_results, today_only)

    return all_events
