
from bidi.algorithm import get_display
import datetime as dt
import json
import time

from typing import Optional, List


class Event:
    def __init__(
        self,
        summary: str,
        unix_time: float,
        end_time: float,
        location: str,
    ):
        self.summary = summary
        self.unix_time = unix_time
        self.end_time = end_time
        self.location = location

    def get_datetime(self):
        return dt.datetime.fromtimestamp(self.unix_time)

    def get_string(self, limit_char: int, date_format: str) -> str:
        event_datetime = self.get_datetime()

        result = str(get_display(self.summary))

        if 0 <= limit_char < len(result):
            result = "".join([c for c in result][:limit_char]) + "..."

        if self.is_today():
            return f"{event_datetime:%H:%M} " + result
        elif self.is_tomorrow():
            return f"{event_datetime:Tomorrow at %H:%M} " + result
        elif self.is_this_week():
            return f"{event_datetime:%a at %H:%M} " + result
        else:
            return f"{event_datetime:{date_format} at %H:%M} " + result

    def is_today(self):
        today = dt.datetime.today()
        return self.get_datetime().date() == today.date()

    def is_tomorrow(self):
        tomorrow = dt.datetime.today() + dt.timedelta(days=1)
        return self.get_datetime().date() == tomorrow.date()

    def is_this_week(self):
        next_week = dt.datetime.today() + dt.timedelta(days=7)
        return self.get_datetime() < next_week.date()

    def is_urgent(self):
        now = dt.datetime.now()
        urgent = now + dt.timedelta(minutes=5)
        five_minutes_started = self.get_datetime() + dt.timedelta(minutes=5)
        # is urgent if it begins in five minutes and if it hasn't passed 5 minutes it started
        return self.get_datetime() < urgent and not now > five_minutes_started

    def is_allday(self) -> bool:
        return self.get_datetime().hour == 0


class EventEncoder(json.JSONEncoder):
    def default(self, o):  # pylint: disable=E0202
        if isinstance(o, Event):
            return o.__dict__
        else:
            return json.JSONEncoder.default(self, o)


def get_closest(events: List[Event], hide_event_after: int) -> Optional[Event]:
    closest = None
    for event in events:
        # Don't show all day events
        if event.is_allday():
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
        dt.datetime.strptime(full_time, event_time_format).astimezone().timetuple()
    )
