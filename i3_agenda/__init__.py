#!/usr/bin/env python3

from __future__ import print_function

import datetime
import subprocess

from bidi.algorithm import get_display

from event import Event, EventEncoder
from config import parser, button
from event_utils import get_closest
from API import getEvents
from cache_utils import load_cache, save_cache

DEFAULT_CAL_WEBPAGE = "https://calendar.google.com/calendar/r/day"


def button_action(button_code: str, closest: Event):
    if button_code != "":
        if button_code == "1":
            print("Opening calendar page...")
            subprocess.Popen(["xdg-open", DEFAULT_CAL_WEBPAGE])
        elif button_code == "3":
            print("Opening location link...")
            subprocess.Popen(["xdg-open", closest.location])


def main():
    args = parser.parse_args()

    allowed_calendars_ids = args.ids

    events = None
    if not args.update:
        events = load_cache(args.cachettl)
    if events is None:
        events = getEvents(args.credentials, allowed_calendars_ids, args.maxres, args.today)
        save_cache(events)

    closest = get_closest(events, args.hide_event_after)
    if closest is None:
        print(args.no_event_text)
        return

    button_action(button, closest)

    event_datetime = datetime.datetime.fromtimestamp(closest.unix_time)
    today = datetime.datetime.today()
    tomorrow = today + datetime.timedelta(days=1)
    next_week = today + datetime.timedelta(days=7)
    urgent = today + datetime.timedelta(minutes=5)

    result = str(get_display(closest.summary))

    if 0 <= args.limchar < len(result):
        result = "".join([c for c in result][:args.limchar]) + "..."

    if event_datetime.date() == today.date():
        print(f"{event_datetime:%H:%M} " + result)
        if event_datetime < urgent:
            # special i3blocks exit code to set the block urgent
            exit(33)
    elif event_datetime.date() == tomorrow.date():
        print(f"{event_datetime:Tomorrow at %H:%M} " + result)
    elif event_datetime.date() < next_week.date():
        print(f"{event_datetime:%a at %H:%M} " + result)
    else:
        print(f"{event_datetime:{args.date_format} at %H:%M} " + result)


if __name__ == "__main__":
    main()
