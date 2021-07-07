#!/usr/bin/env python3

from __future__ import print_function

import datetime
import subprocess

from bidi.algorithm import get_display
from typing import List

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


def get_events(args) -> List[Event]:
    events = None
    if not args.update:
        events = load_cache(args.cachettl)
    if events is None:
        events = getEvents(args.credentials, args.ids, args.maxres, args.today)
        save_cache(events)
    return events


def get_event_string(closest: Event, args) -> str:
    event_datetime = closest.get_datetime()

    result = str(get_display(closest.summary))

    if 0 <= args.limchar < len(result):
        result = "".join([c for c in result][:args.limchar]) + "..."

    if closest.is_today():
        return f"{event_datetime:%H:%M} " + result
    elif closest.is_tomorrow():
        return f"{event_datetime:Tomorrow at %H:%M} " + result
    elif closest.is_this_week():
        return f"{event_datetime:%a at %H:%M} " + result
    else:
        return f"{event_datetime:{args.date_format} at %H:%M} " + result


def main():
    args = parser.parse_args()

    events = get_events(args)

    closest = get_closest(events, args.hide_event_after)
    if closest is None:
        print(args.no_event_text)
        return

    button_action(button, closest)

    print(get_event_string(closest, args))

    if closest.is_urgent():
        # special i3blocks exit code to set the block urgent
        exit(33)


if __name__ == "__main__":
    main()
