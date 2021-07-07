
import json
import datetime


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
        return datetime.datetime.fromtimestamp(self.unix_time)

    def is_today(self):
        today = datetime.datetime.today()
        return self.get_datetime().date() == today.date()

    def is_tomorrow(self):
        tomorrow = datetime.datetime.today() + datetime.timedelta(days=1)
        return self.get_datetime().date() == tomorrow.date()

    def is_this_week(self):
        next_week = datetime.datetime.today() + datetime.timedelta(days=7)
        return self.get_datetime() < next_week.date()

    def is_urgent(self):
        urgent = datetime.datetime.today() + datetime.timedelta(minutes=5)
        return self.get_datetime() < urgent


class EventEncoder(json.JSONEncoder):
    def default(self, o):  # pylint: disable=E0202
        if isinstance(o, Event):
            return o.__dict__
        else:
            return json.JSONEncoder.default(self, o)
