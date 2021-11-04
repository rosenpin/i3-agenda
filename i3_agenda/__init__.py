#!/usr/bin/env python3

from __future__ import print_function

import subprocess
import config

from typing import List, Optional
import datetime

from event import Event, get_closest, sort_events, get_future_events

DEFAULT_CAL_WEBPAGE = "https://calendar.google.com/calendar/r/day"


def button_action(button_code: str, closest: Event):
    if button_code != "":
        if button_code == "1":
            print("Opening calendar page...")
            subprocess.Popen(["xdg-open", DEFAULT_CAL_WEBPAGE])
        elif button_code == "3":
            print("Opening location link...")
            subprocess.Popen(["xdg-open", closest.location])


def filter_only_todays_events(events: List[Event]) -> Optional[List[Event]]:
    now = datetime.datetime.utcnow()
    midnight_rfc3339 = now.replace(hour=23, minute=59, second=59)
    return list(
        filter(
            lambda event: datetime.datetime.fromtimestamp(event.start_time)
            < midnight_rfc3339,
            events,
        )
    )


def load_events(args) -> List[Event]:
    from API import get_events
    from cache_utils import load_cache, save_cache

    events = []
    if not args.update:
        events = load_cache(args.cachettl)
        if args.today:
            if events:
                events = filter_only_todays_events(events)

    if events is None:
        events = get_events(args.credentials, args.ids, args.maxres, args.today)
        save_cache(events)
    return events


def main():
    args = config.parser.parse_args()
    config.CONF_DIR = args.conf

    events = load_events(args)

    events = get_future_events(events, args.hide_event_after)

    if args.skip > 0:
        events = sort_events(events)
        events = events[args.skip :]

    closest = get_closest(events)
    if closest is None:
        print(args.no_event_text)
        return

    button_action(config.button, closest)

    print(closest.get_string(args.limchar, args.date_format, args.ongoing_time_left))

    if closest.is_urgent():
        # special i3blocks exit code to set the block urgent
        exit(33)


if __name__ == "__main__":
    main()
