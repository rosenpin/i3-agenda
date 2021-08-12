#!/usr/bin/env python3

from __future__ import print_function

import subprocess

from typing import List

from event import Event, EventEncoder, get_closest
from config import parser, button
from API import get_events
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


def load_events(args) -> List[Event]:
    events = None
    if not args.update:
        events = load_cache(args.cachettl)
    if events is None:
        events = get_events(args.credentials, args.ids, args.maxres, args.today)
        save_cache(events)
    return events


def main():
    args = parser.parse_args()

    events = load_events(args)

    closest = get_closest(events, args.hide_event_after)
    if closest is None:
        print(args.no_event_text)
        return

    button_action(button, closest)

    print(closest.get_string(args.limchar, args.date_format))

    if closest.is_urgent():
        # special i3blocks exit code to set the block urgent
        exit(33)


if __name__ == "__main__":
    main()
