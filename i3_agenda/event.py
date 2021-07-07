
import json


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


class EventEncoder(json.JSONEncoder):
    def default(self, o):  # pylint: disable=E0202
        if isinstance(o, Event):
            return o.__dict__
        else:
            return json.JSONEncoder.default(self, o)
