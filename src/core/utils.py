import re
from datetime import timedelta, timezone
from typing import Optional

from constants.timezone import MOSCOW_TIME_OFFSET


def get_timezone_from_str(tz_string: Optional[str]) -> timezone:
    """Returns timezone based on user.timezone."""
    if tz_string is None:
        return timezone(timedelta(hours=MOSCOW_TIME_OFFSET))

    tz_pattern = r"UTC(?P<sign>[\+|\-])(?P<hours>\d{2}):(?P<minutes>\d{2})"
    sign, hours, minutes = re.search(tz_pattern, tz_string).groups()
    tz_delta = timedelta(hours=int(hours), minutes=int(minutes))
    return timezone(tz_delta) if sign == "+" else timezone(-tz_delta)


def get_word_case(number, single, few, many):
    num = number % 100
    if 5 <= num <= 20:
        return many
    num = number % 10
    if num == 1:
        return single
    if 2 <= num <= 4:
        return few
    return many


def get_word_genitive(number, single, many):
    num = number % 100
    if 2 <= num <= 20:
        return many
    num = number % 10
    if num == 1:
        return single
    return many
