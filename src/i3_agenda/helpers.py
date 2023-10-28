import datetime as dt
import time
from typing_extensions import LiteralString

from i3_agenda.const import *


def human_delta(tdelta : dt.timedelta) -> str:
    duration = [ 0 ] * 4  # will hold decomposition of tdelta in d, h, m, s
    fmts = ['{d[0]} day(s)', '{d[1]}h', '{d[2]}m', '{d[3]}s']

    total_seconds = int(tdelta.total_seconds())

    # convert total_seconds in d, h, m ,s
    duration[0], rem = divmod(total_seconds, SECONDS_PER_DAY)
    duration[1], rem = divmod(rem, SECONDS_PER_HOUR)
    duration[2], duration[3] = divmod(rem, SECONDS_PER_MINUTE)

    # Keep only format for non null value
    fmt =  ' '.join([ fmts[i] for i in range(len(duration)) if duration[i] > 0])
    if not fmt:
        return "0m"

    return fmt.format(d = duration)



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
