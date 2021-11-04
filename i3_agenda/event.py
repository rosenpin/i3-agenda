import re
import json
import time
import datetime as dt
from bidi.algorithm import get_display

from typing import Optional, List
from config import URL_REGEX


class Event:
    def __init__(
        self,
        summary: str,
        start_time: float,
        end_time: float,
        location: str,
    ):
        self.summary = summary
        self.start_time = start_time
        self.end_time = end_time
        self.location = location

    def get_datetime(self):
        return dt.datetime.fromtimestamp(self.start_time)

    def get_end_datetime(self):
        return dt.datetime.fromtimestamp(self.end_time)

    def get_string(
        self, limit_char: int, date_format: str, ongoing_time_left: bool = False
    ) -> str:
        event_datetime = self.get_datetime()

        result = self.summary
        trimmed = False
        if 0 <= limit_char < len(result):
            trimmed = True
            result = "".join([c for c in result][:limit_char])

        result = str(get_display(result))
        # this is done to preserve RTL while adding the "..." since the get_display is applied after adding the "..."
        if trimmed:
            result += "..."

        if self.is_ongoing():
            if ongoing_time_left:
                time_left = self.get_end_datetime() - dt.datetime.now()
                return f"{result} ({human_delta(time_left)} left)"
            else:
                return f"{result} (ends {self.get_end_datetime():%H:%M})"
        elif self.is_today():
            return f"{event_datetime:%H:%M} {result}"
        elif self.is_tomorrow():
            return f"{event_datetime:Tomorrow at %H:%M} {result}"
        elif self.is_this_week():
            return f"{event_datetime:%a at %H:%M} {result}"
        else:
            return f"{event_datetime:{date_format} at %H:%M} {result}"

    def is_ongoing(self):
        now = dt.datetime.now()
        ongoing = now > self.get_datetime() and not now > self.get_end_datetime()
        return ongoing

    def is_today(self):
        today = dt.datetime.today()
        return self.get_datetime().date() == today.date()

    def is_tomorrow(self):
        tomorrow = dt.datetime.today() + dt.timedelta(days=1)
        return self.get_datetime().date() == tomorrow.date()

    def is_this_week(self):
        next_week = dt.datetime.today() + dt.timedelta(days=7)
        return self.get_datetime().date() < next_week.date()

    def is_urgent(self):
        now = dt.datetime.now()
        urgent = now + dt.timedelta(minutes=5)
        five_minutes_started = self.get_datetime() + dt.timedelta(minutes=5)
        # is urgent if it begins in five minutes and if it hasn't passed 5 minutes it started
        return self.get_datetime() < urgent and not now > five_minutes_started

    def is_allday(self) -> bool:
        time_delta = self.end_time - self.start_time
        # event is considered all day if its start time and end time are both 00:00:00
        # and the time difference between start and finish is divisible by 24
        return self.get_datetime().time() == dt.time(0) and time_delta % 24 == 0


class EventEncoder(json.JSONEncoder):
    def default(self, o):  # pylint: disable=E0202
        if isinstance(o, Event):
            return o.__dict__
        else:
            return json.JSONEncoder.default(self, o)


def human_delta(tdelta):
    d = dict(days=tdelta.days)
    d["hrs"], rem = divmod(tdelta.seconds, 3600)
    d["min"], d["sec"] = divmod(rem, 60)

    if d["min"] == 0:
        fmt = "0m"
    elif d["hrs"] == 0:
        fmt = "{min}m"
    elif d["days"] == 0:
        fmt = "{hrs}h {min}m"
    else:
        fmt = "{days} day(s) {hrs}h {min}m"

    return fmt.format(**d)


def sort_events(events: List[Event]) -> List[Event]:
    return sorted(events, key=lambda e: e.start_time, reverse=False)


def get_future_events(events: List[Event], hide_event_after: int) -> List[Event]:
    future_events = []
    now = time.time()

    for event in events:
        # Don't show all day events
        if event.is_allday():
            continue

        now = time.time()
        # If the event already ended
        if event.end_time < now:
            continue

        # If the event started more than hide_event_after ago
        if hide_event_after > -1 and event.start_time + 60 * hide_event_after < now:
            continue

        future_events.append(event)

    return future_events


def get_closest(events: List[Event]) -> Optional[Event]:
    closest = None
    for event in events:
        if closest is None or event.start_time < closest.start_time:
            closest = event

    return closest


def get_unix_time(full_time: str) -> float:
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


def from_json(event_json) -> Event:
    end_time = get_unix_time(
        event_json["end"].get("dateTime", event_json["end"].get("date"))
    )
    start_time = event_json["start"].get("dateTime", event_json["start"].get("date"))
    start_time = get_unix_time(start_time)

    location = None

    if "location" in event_json:
        location = event_json["location"]
    elif "description" in event_json:
        matches = re.findall(URL_REGEX, event_json["description"])
        location = matches[0][0] if matches else None

    return Event(event_json["summary"], start_time, end_time, location)
