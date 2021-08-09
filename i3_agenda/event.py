
import json
import datetime as dt
from bidi.algorithm import get_display


class Event:
    def __init__(
        self,
        summary: str,
        is_allday: bool,
        unix_time: float,
        end_time: float,
        location: str,
    ):
        self.is_allday = is_allday
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


class EventEncoder(json.JSONEncoder):
    def default(self, o):  # pylint: disable=E0202
        if isinstance(o, Event):
            return o.__dict__
        else:
            return json.JSONEncoder.default(self, o)
