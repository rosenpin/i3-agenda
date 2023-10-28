
import datetime as dt

import pytest

from typing import Dict

from i3_agenda.helpers import *


@pytest.mark.parametrize("test_input,expected",
[
    ({"minutes":0}, "0m"),
    ({"minutes":1}, "1m"),
    ({"hours":1}, "1h"),
    ({"days":1}, "1 day(s)"),
    ({"days":1, "hours":1, "minutes":1}, "1 day(s) 1h 1m"),
    ({"hours":23, "minutes":59}, "23h 59m"),
]
)
def test_human_delta(test_input:Dict[str,int],expected:str):
    assert human_delta(dt.timedelta(**test_input)) == expected

