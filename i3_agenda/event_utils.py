
import time
import datetime
from typing import Optional, List

from event import Event


def get_closest(events: List[Event], hide_event_after: int) -> Optional[Event]:
    closest = None
    for event in events:
        # Don't show all day events
        if event.is_allday:
            continue

        now = time.time()
        # If the event already ended
        if event.end_time < now:
            continue

        # If the event started more than hide_event_after ago
        if hide_event_after > -1 and event.unix_time + 60 * hide_event_after < now:
            continue

        if closest is None or event.unix_time < closest.unix_time:
            closest = event

    return closest


def get_event_time(full_time: str) -> float:
    if "T" in full_time:
        event_time_format = "%Y-%m-%dT%H:%M:%S%z"
    else:
        event_time_format = "%Y-%m-%d"

    # Python introduced the ability to parse ":" in the timezone format (in strptime()) only from version 3.7 and up.
    # We need to remove the : before the timezone to support older versions
    # See https://stackoverflow.com/questions/30999230/how-to-parse-timezone-with-colon for more information
    if full_time[-3] == ":":
        full_time = full_time[:-3] + full_time[-2:]

    return time.mktime(
        datetime.datetime.strptime(full_time, event_time_format).astimezone().timetuple()
    )


def is_allday(start_time: str) -> bool:
    return "T" not in start_time
