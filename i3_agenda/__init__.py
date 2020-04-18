#!/usr/bin/env python3

from __future__ import print_function

import argparse
import datetime
import json
import os
import os.path
import pickle
import subprocess
import time
from os.path import expanduser

from bidi.algorithm import get_display
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

CONF_DIR = expanduser('~') + os.path.sep + ".i3agenda"
TMP_TOKEN = f"{CONF_DIR}/i3agenda_google_token.pickle"
CACHE_PATH = f"{CONF_DIR}/i3agenda_cache.txt"
SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']
DEFAULT_CAL_WEBPAGE = 'https://calendar.google.com/calendar/r/day'

# i3blocks use this envvar to check the click
button = os.getenv("BLOCK_BUTTON", "")  

parser = argparse.ArgumentParser(description='Show next Google Calendar event')
parser.add_argument('--credentials',
                    '-c',
                    type=str,
                    default='',
                    help='path to your credentials.json file')
parser.add_argument('--cachettl',
                    '-ttl',
                    type=int,
                    default=30,
                   help='time for cache to be kept in minutes')
parser.add_argument('--today',
                    '-d',
                    default=False,
                    help='print only today events')
parser.add_argument('--ids',
                    '-i',
                    type=str,
                    default=[],
                    nargs='+',
                    help='list of calendar ids to fetch, space separated. If none is specified all calendars will be fetched')
parser.add_argument('--maxres',
                    '-r',
                    type=int,
                    default=10, 
                    help='max number of events to query Google\'s API for each of your calendars. Increase this number if you have lot of events in your google calendar')

class Event():
    def __init__(self, summary, is_allday, unix_time, end_time):
        self.is_allday = is_allday
        self.summary = summary
        self.unix_time = unix_time
        self.end_time = end_time

class EventEncoder(json.JSONEncoder):
    def default(self, o):  # pylint: disable=E0202
        if isinstance(o, Event):
            return o.__dict__
        else:
            return json.JSONEncoder.default(self, o)

def main():
    args = parser.parse_args()

    allowed_calendars_ids = args.ids

    if button != "":
        subprocess.Popen(["xdg-open", DEFAULT_CAL_WEBPAGE])

    events = load_cache(args.cachettl)
    if events == None:
        service = connect(args.credentials)
        events = getEvents(service, allowed_calendars_ids, args.maxres,
                           args.today)
        save_cache(events)

    closest = get_closest(events)
    if closest is None:
        print("No events")
        return

    t = datetime.datetime.fromtimestamp(closest.unix_time)
    print(f"{t:%H:%M} " + get_display(closest.summary))

def getEvents(service, allowed_calendars_ids, max_results, today_only=False):
    now = datetime.datetime.utcnow()
    now_rfc3339= now.isoformat() + 'Z' # 'Z' indicates UTC time
    calendar_ids = []
    while True:
        calendar_list = service.calendarList().list().execute()
        for calendar_list_entry in calendar_list['items']:
            if not allowed_calendars_ids or calendar_list_entry['id'] in allowed_calendars_ids:
                calendar_ids.append(calendar_list_entry['id'])
        page_token = calendar_list.get('nextPageToken')
        if not page_token:
            break

    all = []
    for id in calendar_ids:
        if today_only:
            midnight_rfc3339 = now.replace(hour=23, minute=39, second=59).isoformat() + 'Z'
            events_result = service.events().list(calendarId=id,
                                                timeMin=now_rfc3339,
                                                timeMax=midnight_rfc3339,
                                                maxResults=max_results,
                                                singleEvents=True,
                                                orderBy='startTime').execute()
        else:
            events_result = service.events().list(calendarId=id,
                                                timeMin=now_rfc3339,
                                                maxResults=max_results,
                                                singleEvents=True,
                                                orderBy='startTime').execute()
        events = events_result.get('items', [])

        if not events:
            continue

        for event in events:
            end_time = get_event_time(event['end'].get('dateTime', event['end'].get('date')))
            start_time = event['start'].get('dateTime', event['start'].get('date'))
            unix_time = get_event_time(start_time)
            all.append(Event(event['summary'], is_allday(start_time), unix_time, end_time))

    return all


def is_allday(start_time) -> bool:
    return "T" not in start_time


def get_event_time(full_time):
    if "T" in full_time:
        format = '%Y-%m-%dT%H:%M:%S%z'
    else:
        format = '%Y-%m-%d'

    # Python introduced the ability to parse ":" in the timezone format (in strptime()) only from version 3.7 and up.
    # We need to remove the : before the timezone to support older versions
    # See https://stackoverflow.com/questions/30999230/how-to-parse-timezone-with-colon for more information
    if full_time[-3] == ":":
        full_time = full_time[:-3] + full_time[-2:]

    return time.mktime(
        datetime.datetime.strptime(full_time, format).astimezone().timetuple())


def get_closest(events) -> Event:
    closest = None
    for event in events:
        # Don't show all day events
        if event.is_allday:
            continue

        # If the event already ended
        if event.end_time < time.time():
            continue

        if closest is None or event.unix_time < closest.unix_time:
            closest = event

    return closest


def load_cache(cachettl):
    if not os.path.exists(CACHE_PATH):
        return None

    if os.path.getmtime(CACHE_PATH) - time.time() > cachettl * 60:
        return None

    events = []

    try:
        with open(CACHE_PATH, 'r') as f:
            raw = json.loads(f.read())
            for event in raw:
                events.append(
                    Event(event['summary'], event['is_allday'], event['unix_time'], event['end_time'])
                )
        return events
    except Exception:
        # Invalid cache
        return None


def save_cache(events):
    with open(CACHE_PATH, 'w+') as f:
        f.write(EventEncoder().encode(events))


def connect(credspath):
    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if not os.path.exists(CONF_DIR):
        os.mkdir(CONF_DIR)
    if os.path.exists(TMP_TOKEN):
        with open(TMP_TOKEN, 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if not os.path.exists(credspath):
            print(
                "You need to download your credentials json file from the Google API Console and pass its path to this script"
            )
            exit(1)
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(credspath, SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open(TMP_TOKEN, 'wb') as token:
            pickle.dump(creds, token)

    service = build('calendar', 'v3', credentials=creds)
    return service


if __name__ == '__main__':
    main()
