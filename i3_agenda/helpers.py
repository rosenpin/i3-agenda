import datetime as dt
import time
from typing_extensions import LiteralString

from const import *


def human_delta(tdelta : dt.timedelta) -> LiteralString:
    d : dict[str, int] = dict(days=tdelta.days)
    d["hrs"], rem = divmod(tdelta.seconds, SECONDS_PER_HOUR)
    d["min"], d["sec"] = divmod(rem, SECONDS_PER_MINUTE)

    if d["min"] == 0:
        fmt = "0m"
    elif d["hrs"] == 0:
        fmt = "{min}m"
    elif d["days"] == 0:
        fmt = "{hrs}h {min}m"
    else:
        fmt = "{days} day(s) {hrs}h {min}m"

    return fmt.format(**d)

def make_tz_backward_compatible(full_time : str) -> str:
    # Python introduced the ability to parse ":" in the timezone format (in strptime()) only from version 3.7 and up.
    # We need to remove the : before the timezone to support older versions
    # See https://stackoverflow.com/questions/30999230/how-to-parse-timezone-with-colon for more information
    if full_time[-3] == ":":
        full_time = full_time[:-3] + full_time[-2:]
    return full_time

def get_unix_time(full_time: str) -> float:
    if "T" in full_time:
        event_time_format = "%Y-%m-%dT%H:%M:%S%z"
    else:
        event_time_format = "%Y-%m-%d"

    full_time = make_tz_backward_compatible(full_time)

    return time.mktime(
        dt.datetime.strptime(full_time, event_time_format).astimezone().timetuple()
    )
