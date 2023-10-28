import datetime as dt
import json
import re
import time
from typing import List, Optional, Any, Union, Dict


from bidi.algorithm import get_display

from i3_agenda.config import MIN_CHARS, MIN_DELAY, URL_REGEX
from i3_agenda.const import *
from i3_agenda.helpers import get_unix_time, human_delta
from dataclasses import dataclass



@dataclass
class Event:
    summary: str
    start_time: int
    end_time: int
    location: Union[str, None]


    def get_datetime(self) -> dt.datetime:
        return dt.datetime.fromtimestamp(self.start_time)

    def get_end_datetime(self) -> dt.datetime:
        return dt.datetime.fromtimestamp(self.end_time)

    def get_string(
        self,
        limit_char: int,
        date_format: str,
        ongoing_time_left: bool = False,
        next_event_time_left: bool = False,
    ) -> str:
        event_datetime = self.get_datetime()

        result = self.summary
        trimmed = ""
        if MIN_CHARS < limit_char < len(result):
            trimmed = "".join([c for c in result][:limit_char])

        # this is done to preserve RTL while adding the "..." since the get_display is applied after adding the "..."
        if trimmed:
            result = trimmed + "..."
        result = str(get_display(result))

        if self.is_ongoing():
            if ongoing_time_left:
                time_left = self.get_end_datetime() - dt.datetime.now()
                return f"{result} ({human_delta(time_left)} left)"
            else:
                return f"{result} (ends {self.get_end_datetime():%H:%M})"
        elif self.is_today():
            if not self.is_ongoing() and next_event_time_left:
                time_left = event_datetime - dt.datetime.now()
                return f"{result} in {human_delta(time_left)}"
            else:
                return f"{event_datetime:%H:%M} {result}"
        elif self.is_tomorrow():
            return f"{event_datetime:Tomorrow at %H:%M} {result}"
        elif self.is_this_week():
            return f"{event_datetime:%a at %H:%M} {result}"
        else:
            return f"{event_datetime:{date_format} at %H:%M} {result}"

    def is_ongoing(self) -> bool:
        now = dt.datetime.now()
        ongoing = now > self.get_datetime() and not now > self.get_end_datetime()
        return ongoing

    def is_today(self) -> bool:
        today = dt.datetime.today()
        return self.get_datetime().date() == today.date()

    def is_tomorrow(self) -> bool:
        tomorrow = dt.datetime.today() + dt.timedelta(days=1)
        return self.get_datetime().date() == tomorrow.date()

    def is_this_week(self) -> bool:
        today = dt.datetime.today()
        next_week = today + dt.timedelta(days=DAYS_PER_WEEK)
        return today.date() <= self.get_datetime().date() < next_week.date()


    def is_urgent(self) -> bool:
        now = dt.datetime.now()
        urgent = now + dt.timedelta(minutes=URGENT_DELAY_MN)
        five_minutes_started = self.get_datetime() + dt.timedelta(minutes=URGENT_DELAY_MN)
        # is urgent if it begins in URGENT_DELAY_MN minutes and if it hasn't
        # passed URGENT_DELAY_MN minutes it started
        return self.get_datetime() < urgent and not now > five_minutes_started

    def is_allday(self) -> bool:
        time_delta = self.end_time - self.start_time
        # event is considered all day if its start time and end time are both 00:00:00
        # and the time difference between start and finish is divisible by 24
        return self.get_datetime().time() == dt.time(0) \
                and self.get_end_datetime().time() == dt.time(0) \
                and time_delta % SECONDS_PER_DAY == 0



class EventEncoder(json.JSONEncoder):
    def default(self, o):  # pylint: disable=E0202
        if isinstance(o, Event):
            return o.__dict__
        else:
            return json.JSONEncoder.default(self, o)




def sort_events(events: List[Event]) -> List[Event]:
    return sorted(events, key=lambda e: e.start_time, reverse=False)


def get_future_events(events: List[Event], hide_event_after: int, show_event_before: int) -> List[Event]:
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

        # Event won't start for more than show_event_before
        if show_event_before > MIN_DELAY and now + SECONDS_PER_MINUTE * show_event_before < event.start_time:
            continue

        # If the event started more than hide_event_after ago
        if hide_event_after > MIN_DELAY and event.start_time + SECONDS_PER_MINUTE * hide_event_after < now:
            continue

        future_events.append(event)

    return future_events


def get_closest(events: List[Event]) -> Optional[Event]:
    closest = None
    for event in events:
        if closest is None or event.start_time < closest.start_time:
            closest = event

    return closest




def from_json(event_json : Dict[str,Any]) -> Event:
    end_time = int(get_unix_time(
        event_json["end"].get("dateTime", event_json["end"].get("date")))
    )
    start_time = event_json["start"].get("dateTime", event_json["start"].get("date"))
    start_time = int(get_unix_time(start_time))

    location = None

    if "location" in event_json:
        location = event_json["location"]
    elif "description" in event_json:
        matches = re.findall(URL_REGEX, event_json["description"])
        location = matches[0][0] if matches else None
    return Event(event_json.get("summary", "(No title)"), start_time, end_time, location)
