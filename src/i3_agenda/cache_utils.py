from i3_agenda.config import CONF_DIR
from typing import Optional, List, TextIO

import os.path
import time
import json

from i3_agenda.event import Event, EventEncoder
from i3_agenda.const import SECONDS_PER_MINUTE

CACHE_PATH = f"{CONF_DIR}/i3agenda_cache.txt"


def load_cache(cachettl: int) -> Optional[List[Event]]:
    if not os.path.exists(CACHE_PATH):
        return None

    if time.time() - os.path.getmtime(CACHE_PATH) > cachettl * SECONDS_PER_MINUTE:
        return None

    try:
        with open(CACHE_PATH, "r") as f:
            events = get_events_from_cache(f)
        return events
    except IOError:
        # Invalid cache
        return None


def save_cache(events: List[Event]):
    with open(CACHE_PATH, "w+") as f:
        f.write(EventEncoder().encode(events))


def get_events_from_cache(f: TextIO):
    events = []
    raw = json.loads(f.read())
    for event in raw:
        try:
            events.append(
                Event(
                    event["summary"],
                    event["start_time"],
                    event["end_time"],
                    event["location"],
                )
            )
        except KeyError:
            # At least one of the events in cache are invalid, must mean that the entire cache is invalid
            return None
    return events
