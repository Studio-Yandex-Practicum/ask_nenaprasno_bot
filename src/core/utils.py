import re
from datetime import timedelta, timezone
from typing import Optional


async def get_timezone_from_str(tz_string: Optional[str]) -> timezone:
    """Returns timezone based on user.timezone."""
    if tz_string is None:
        return timezone.utc

    tz_pattern = r"UTC(?P<sign>[\+|\-])(?P<hours>\d{2}):(?P<minutes>\d{2})"
    sign, hours, minutes = re.search(tz_pattern, tz_string).groups()
    tz_delta = timedelta(hours=int(hours), minutes=int(minutes))
    return timezone(tz_delta) if sign == "+" else timezone(-tz_delta)
