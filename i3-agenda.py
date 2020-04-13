#!/usr/bin/env python3

from __future__ import print_function
import json
from bidi.algorithm import get_display
import time
import datetime
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import argparse
import os
import subprocess

SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']
TMP_TOKEN = '/tmp/i3agenda_google_token.pickle'
CACHE_PATH = '/tmp/i3agenda_cache.txt'
DEFAULT_CAL_WEBPAGE = 'https://calendar.google.com/calendar/r/day'

button = os.getenv("BLOCK_BUTTON", "") # i3blocks use this envvar to check the click

parser = argparse.ArgumentParser(description='Show next Google Calendar event')
parser.add_argument('--credentials', '-c', type=str,
                    default='',
                    help='path to your credentials.json file')
parser.add_argument('--cachettl', '-ttl', type=int, default=30,
                   help='time for cache to be kept in minutes')

class Event():
    def __init__(self, summary, start_time, unix_time, end_time):
        self.start_time = start_time
        self.summary = summary
        self.unix_time = unix_time
        self.end_time = end_time

class EventEncoder(json.JSONEncoder):
   def default(self, object):
    if isinstance(object, Event):
        return object.__dict__
    else:
        return json.JSONEncoder.default(self, object)

def main():
    args = parser.parse_args()

    if button is not "":
        subprocess.Popen(["xdg-open", DEFAULT_CAL_WEBPAGE])
        
    events = load_cache(args.cachettl)
    if events == None:
        service = connect(args.credentials)
        events = getEvents(service)
        save_cache(events)

    closest = get_closest(events)
        
    t = datetime.datetime.fromtimestamp(closest[0])
    print(f"{t:%H:%M} " + get_display(closest[1]) )

def getEvents(service):
    now = datetime.datetime.utcnow().isoformat() + 'Z' # 'Z' indicates UTC time
    calendar_ids = []
    while True:
        calendar_list = service.calendarList().list().execute()
        for calendar_list_entry in calendar_list['items']:
            calendar_ids.append(calendar_list_entry['id'])
        page_token = calendar_list.get('nextPageToken')
        if not page_token:
            break

    all = []
    for id in calendar_ids:
        events_result = service.events().list(calendarId=id, timeMin=now,
                                            maxResults=10, singleEvents=True,
                                            orderBy='startTime').execute()
        events = events_result.get('items', [])

        if not events:
            continue

        for event in events:
            end_time = get_event_time(event['end'].get('dateTime', event['end'].get('date')))
            start_time = event['start'].get('dateTime', event['start'].get('date'))
            unix_time = get_event_time(start_time)
            all.append(Event(event['summary'], start_time, unix_time, end_time))

    return all

def get_event_time(full_time):
    if "T" in full_time:
        format = '%Y-%m-%dT%H:%M:%S%z'
    else: 
        format = '%Y-%m-%d'

    # Python introduced the ability to parse ":" in the timezone format (in strptime()) only from version 3.7 and up.
    # We need to remove the : before the timezone to support older versions
    # See https://stackoverflow.com/questions/30999230/how-to-parse-timezone-with-colon for more information
    if full_time[-3] == ":":
        full_time = full_time[:-3]+full_time[-2:]

    return time.mktime(datetime.datetime.strptime(full_time,
                                                  format).astimezone().timetuple())

def get_closest(events):
    closest = [-1,""]
    for event in events:
        if "T" in event.start_time:
            current = event.unix_time
            if event.end_time < time.time():
                continue
            if closest[0] == -1 or current < closest[0]:
                closest[0] = current
                closest[1] = event.summary

    return closest

def load_cache(cachettl):
    if not os.path.exists(CACHE_PATH):
        return None

    if os.path.getmtime(CACHE_PATH) - time.time() > cachettl * 60:
        return None

    events = []
    with open(CACHE_PATH, 'r') as f:
        raw = json.loads(f.read())
        for event in raw:
            events.append(Event(event['summary'], event['start_time'], event['unix_time'], event['end_time']))
    return events

def save_cache(events):
    with open(CACHE_PATH, 'w+') as f:
        f.write(EventEncoder().encode(events))

def connect(credspath):
    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists(TMP_TOKEN):
        with open(TMP_TOKEN, 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if not os.path.exists(credspath):
            print("You need to download your credentials json file from the Google API Console and pass its path to this script")
            exit(1)
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                credspath, SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open(TMP_TOKEN, 'wb') as token:
            pickle.dump(creds, token)

    service = build('calendar', 'v3', credentials=creds)
    return service

if __name__ == '__main__':
    main()
