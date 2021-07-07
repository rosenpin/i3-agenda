
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
    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if not os.path.exists(CONF_DIR):
        os.mkdir(CONF_DIR)
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

    service = build("calendar", "v3", credentials=creds)
    return service


def getEvents(
        credentials: str, allowed_calendars_ids: List[str], max_results: int, today_only=False
) -> List[Event]:
    service = connect(credentials)

    now = datetime.datetime.utcnow()
    now_rfc3339 = now.isoformat() + "Z"  # 'Z' indicates UTC time
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

    all_events = []
    for calendar_id in calendar_ids:
        if today_only:
            midnight_rfc3339 = (
                    now.replace(hour=23, minute=39, second=59).isoformat() + "Z"
            )
            events_result = (
                service.events()
                .list(
                    calendarId=calendar_id,
                    timeMin=now_rfc3339,
                    timeMax=midnight_rfc3339,
                    maxResults=max_results,
                    singleEvents=True,
                    orderBy="startTime",
                )
                .execute()
            )
        else:
            events_result = (
                service.events()
                .list(
                    calendarId=calendar_id,
                    timeMin=now_rfc3339,
                    maxResults=max_results,
                    singleEvents=True,
                    orderBy="startTime",
                )
                .execute()
            )
        events = events_result.get("items", [])

        if not events:
            continue

        for event in events:
            end_time = get_event_time(
                event["end"].get("dateTime", event["end"].get("date"))
            )
            start_time = event["start"].get("dateTime", event["start"].get("date"))
            unix_time = get_event_time(start_time)

            location = None

            if "location" in event:
                location = event["location"]
            elif "description" in event:
                matches = re.findall(URL_REGEX, event["description"])
                location = matches[0][0] if matches else None

            all_events.append(
                Event(
                    event["summary"],
                    is_allday(start_time),
                    unix_time,
                    end_time,
                    location,
                )
            )

    return all_events
