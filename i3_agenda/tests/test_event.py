import datetime as dt
import os
import time

from freezegun import freeze_time
import pytest

from event import *


os.environ['TZ'] = 'UTC'
time.tzset()

def new_event(start_time: str, end_time: str, summary="summary", location=None):
    start = dt.datetime.strptime(start_time, "%Y-%m-%d %H:%M:%S")
    end = dt.datetime.strptime(end_time, "%Y-%m-%d %H:%M:%S")
    return Event(summary, int(start.timestamp()), int(end.timestamp()), location)


@pytest.mark.parametrize(
    "start,end,expected",
    [
        ("2022-12-14 12:00:07", "2022-12-14 12:05:07", True),
        ("2022-12-13 12:00:07", "2022-12-13 12:05:07", False),  # Before
        ("2022-12-15 12:00:07", "2022-12-15 12:05:07", False),  # After
    ],
)
@freeze_time("2022-12-14 12:03:07")
def test_is_ongoing(start, end, expected):
    assert new_event(start, end).is_ongoing() == expected


@pytest.mark.parametrize(
    "start,end,expected",
    [
        ("2022-12-14 12:00:07", "2022-12-14 12:05:07", True),
        ("2022-12-14 12:00:07", "2022-12-15 12:05:07", True),
        ("2022-12-13 12:00:07", "2022-12-14 12:05:07", False),
        ("2022-12-13 12:00:07", "2022-12-13 12:05:07", False),
    ],
)
@freeze_time("2022-12-14 12:03:07")
def test_is_today(start, end, expected):
    assert new_event(start, end).is_today() == expected


@pytest.mark.parametrize(
    "start,end,expected",
    [
        ("2022-12-15 12:00:07", "2022-12-15 12:05:07", True),
        ("2022-12-15 12:00:07", "2022-12-17 12:05:07", True),
        ("2022-12-14 12:00:07", "2022-12-14 12:05:07", False),
        ("2022-12-14 12:00:07", "2022-12-15 12:05:07", False),
        ("2022-12-13 12:00:07", "2022-12-14 12:05:07", False),
        ("2022-12-13 12:00:07", "2022-12-13 12:05:07", False),
    ],
)
@freeze_time("2022-12-14 12:03:07")
def test_is_tomorrow(start, end, expected):
    assert new_event(start, end).is_tomorrow() == expected


@pytest.mark.parametrize(
    "start,end,expected",
    [
        ("2022-12-14 12:00:07", "2022-12-15 12:05:07", True),
        ("2022-12-14 12:00:07", "2022-12-26 12:05:07", True),
        ("2022-12-20 12:00:07", "2022-12-26 12:05:07", True),
        ("2022-12-22 12:00:07", "2022-12-26 12:05:07", False),
        ("2022-12-14 11:00:07", "2022-12-15 12:05:07", True),
        ("2022-12-13 11:00:07", "2022-12-15 12:05:07", False),
    ],
)
@freeze_time("2022-12-14 12:03:07")
def test_is_this_week(start, end, expected):
    assert new_event(start, end).is_this_week() == expected


@pytest.mark.parametrize(
    "start,end,expected",
    [
        ("2022-12-14 12:09:07", "2022-12-15 12:35:07", True),
        ("2022-12-14 12:05:06", "2022-12-15 12:35:07", False),  # Just before now - 5m
        ("2022-12-14 12:05:08", "2022-12-15 12:35:07", True),  # Just after now - 5m
        ("2022-12-14 12:15:06", "2022-12-15 12:35:07", True),  # Just before now + 5m
        ("2022-12-14 12:15:08", "2022-12-15 12:35:07", False),  # After now + 5m
    ],
)
@freeze_time("2022-12-14 12:10:07")
def test_is_urgent(start, end, expected):
    assert new_event(start, end).is_urgent() == expected


@pytest.mark.parametrize(
    "start,end,expected",
    [
        ("2022-12-14 00:00:00", "2022-12-15 00:00:00", True),
        ("2022-12-14 12:05:06", "2022-12-15 12:35:07", False),
        ("2022-12-14 00:00:00", "2022-12-18 00:00:00", True),
        ("2022-12-14 00:00:00", "2023-12-18 00:00:00", True),
        ("2022-12-14 00:00:00", "2023-12-14 00:00:24", False),
        ("2022-12-14 00:00:00", "2022-12-18 00:00:24", False),
    ],
)
@freeze_time("2022-12-14 12:10:07")
def test_is_allday(start, end, expected):
    assert new_event(start, end).is_allday() == expected


@freeze_time("2022-12-14 12:10:07")
def test_get_future_events_without_after_before():
    events = [
        new_event("2022-12-15 00:00:00", "2022-12-18 00:00:00"),  # all day
        new_event("2022-12-13 00:00:00", "2022-12-13 03:00:00"),  # finished
        new_event("2022-12-14 12:00:00", "2022-12-14 15:00:00"),  # in middle
        new_event("2022-12-14 15:00:00", "2022-12-14 17:00:00"),  # future
    ]
    # It should only keep the two last
    expected = events[-2:]
    assert get_future_events(events, MIN_DELAY, MIN_DELAY) == expected


@freeze_time("2022-12-14 12:10:07")
def test_get_future_events_with_after():
    events = [
        new_event("2022-12-15 00:00:00", "2022-12-18 00:00:00"),  # all day
        new_event("2022-12-13 00:00:00", "2022-12-13 03:00:00"),  # finished
        new_event(
            "2022-12-14 12:00:00", "2022-12-14 15:00:00"
        ),  # in middle more than 5m
        new_event(
            "2022-12-14 12:06:00", "2022-12-14 15:00:00"
        ),  # in middle less than 5m
        new_event("2022-12-14 15:00:00", "2022-12-14 17:00:00"),  # future
    ]
    # It should only keep the two last
    expected = events[-2:]
    assert get_future_events(events, 5, MIN_DELAY) == expected


@freeze_time("2022-12-14 12:10:07")
def test_get_future_events_with_before():
    events = [
        new_event("2022-12-15 00:00:00", "2022-12-18 00:00:00"),  # all day
        new_event("2022-12-13 00:00:00", "2022-12-13 03:00:00"),  # finished
        new_event("2022-12-15 15:00:00", "2022-12-15 17:00:00"),  # distant future
        new_event("2022-12-14 12:15:08", "2022-12-14 17:00:00"),  # future after 5m
        new_event("2022-12-14 12:00:00", "2022-12-14 15:00:00"),  # in middle
        new_event("2022-12-14 12:15:06", "2022-12-14 17:00:00"),  # future before 5m
    ]
    # It should only keep the two  last
    expected = events[-2:]
    assert get_future_events(events, MIN_DELAY, 5) == expected


def test_get_closest():
    events = [
        new_event("2022-12-15 00:00:00", "2022-12-18 00:00:00"),
        new_event("2022-12-13 00:00:00", "2022-12-13 03:00:00"),
        new_event("2022-12-15 15:00:00", "2022-12-15 17:00:00"),
        new_event("2022-12-14 12:15:08", "2022-12-14 17:00:00"),
        new_event("2022-12-14 12:00:00", "2022-12-14 15:00:00"),
        new_event("2022-11-14 12:15:06", "2022-12-14 17:00:00"),  # closest
    ]
    expected = events[-1]
    assert get_closest(events) == expected


@pytest.mark.parametrize(
    "json,expected",
    [
        # Test with a basic input
        (
            {
                "summary": "Test event",
                "start": {"dateTime": "2022-12-05T15:00:00+0000"},
                "end": {"dateTime": "2022-12-05T17:00:00+0000"},
                "location": "Test location",
            },
            Event("Test event", 1670252400, 1670259600, "Test location"),
        ),
        # Test with a different time format
        (
            {
                "summary": "Test event",
                "start": {"date": "2022-12-05"},
                "end": {"date": "2022-12-06"},
                "location": "Test location",
            },
            Event("Test event", 1670198400, 1670284800, "Test location"),
        ),
        # Test with no title
        (
            {
                "start": {"dateTime": "2022-12-05T15:00:00+0100"},
                "end": {"dateTime": "2022-12-05T17:00:00+0100"},
                "location": "Test location",
            },
            Event("(No title)", 1670248800, 1670256000, "Test location"),
        ),
        # Test with a description but no location
        (
            {
                "summary": "Test event",
                "start": {"dateTime": "2022-12-05T15:00:00+0000"},
                "end": {"dateTime": "2022-12-05T17:00:00+0000"},
                "description": "This is a test description with no location.",
            },
            Event("Test event", 1670252400, 1670259600, None),
        ),
        # Test with a location within description
        (
            {
                "summary": "Test event",
                "start": {"dateTime": "2022-12-05T15:00:00+0000"},
                "end": {"dateTime": "2022-12-05T17:00:00+0000"},
                "description": "This is a test description with url : https://truc.com/calendar/ezfzerazdfz.",
            },
            Event(
                "Test event",
                1670252400,
                1670259600,
                "https://truc.com/calendar/ezfzerazdfz.",
            ),
        ),
    ],
)
def test_from_json(json, expected):
    assert from_json(json) == expected


now = dt.datetime.strptime("2022-12-14 12:10:06+0000", "%Y-%m-%d %H:%M:%S%z")


@pytest.mark.parametrize(
    "event_params,otl,netl,expected",
    [
        # Test event that is ongoing as 1 hour left and ongoing_time_left is True
        (
            dict(
                summary="Event 1",
                start_time=now.timestamp(),
                end_time=(now + dt.timedelta(hours=1, seconds=1)).timestamp(),
                location=None,
            ),
            True,
            False,
            "Event 1 (1h left)",
        ),
        # Test event that is not ongoing and is today and next_event_time_left is True
        (
            dict(
                summary="Event 1",
                start_time=(now + dt.timedelta(minutes=30, seconds=1)).timestamp(),
                end_time=(now + dt.timedelta(hours=1, seconds=1)).timestamp(),
                location=None,
            ),
            False,
            True,
            "Event 1 in 30m",
        ),
        # Test event that is not ongoing and is today and next_event_time_left is True
        (
            dict(
                summary="Event 1",
                start_time=(now + dt.timedelta(minutes=30, seconds=1)).timestamp(),
                end_time=(now + dt.timedelta(hours=1, seconds=1)).timestamp(),
                location=None,
            ),
            True,
            False,
            "12:40 Event 1",
        ),
        # Test event that is not ongoing and is today and next_event_time_left is True
        (
            dict(
                summary="Event 1",
                start_time=(now + dt.timedelta(minutes=30, seconds=1)).timestamp(),
                end_time=(now + dt.timedelta(hours=1, seconds=1)).timestamp(),
                location=None,
            ),
            False,
            False,
            "12:40 Event 1",
        ),
        # Test event that is not ongoing and is tomorrow
        (
            dict(
                summary="Event 1",
                start_time=(now + dt.timedelta(days=1, seconds=1)).timestamp(),
                end_time=(now + dt.timedelta(hours=1, seconds=1)).timestamp(),
                location=None,
            ),
            False,
            False,
            "Tomorrow at 12:10 Event 1",
        ),
        # Test event that is not ongoing, not tommorrow and this week
        (
            dict(
                summary="Event 1",
                start_time=(now + dt.timedelta(days=2, seconds=1)).timestamp(),
                end_time=(now + dt.timedelta(hours=1, seconds=1)).timestamp(),
                location=None,
            ),
            False,
            False,
            "Fri at 12:10 Event 1",
        ),
        # Test event that is not ongoing, not tommorrow and after this week
        (
            dict(
                summary="Event 1",
                start_time=(now + dt.timedelta(days=8, seconds=1)).timestamp(),
                end_time=(now + dt.timedelta(hours=1, seconds=1)).timestamp(),
                location=None,
            ),
            False,
            False,
            "2022-12-22 at 12:10 Event 1",
        ),
    ],
)
@freeze_time(now + dt.timedelta(seconds=1))
def test_get_string(event_params, otl: bool, netl: bool, expected):

    event = Event(**event_params)
    result = event.get_string(
        limit_char=100,
        date_format="%Y-%m-%d",
        ongoing_time_left=otl,
        next_event_time_left=netl,
    )
    assert result == expected

@pytest.mark.parametrize(
    "description, expected", [
        ("A string that has more than twenty chars", "2022-12-22 at 12:10 A string that has mo..."),
        ("اجراجوییِ تازه مغامرة جديدة", "2022-12-22 at 12:10 ...رماغم هزات ِییوجارجا"), # An RTL string
        ("הרפתקה חדשה הרפתקה חדשה", "2022-12-22 at 12:10 ...ח הקתפרה השדח הקתפרה") # An RTL string
    ])
@freeze_time(now + dt.timedelta(seconds=1))
def test_get_string_description(description, expected):

    event = Event(
                summary=description,
                start_time=(now + dt.timedelta(days=8, seconds=1)).timestamp(),
                end_time=(now + dt.timedelta(hours=1, seconds=1)).timestamp(),
                location=None,
                )
    result = event.get_string(
        limit_char=20,
        date_format="%Y-%m-%d",
        ongoing_time_left=False,
        next_event_time_left=False,
    )
    assert result == expected
