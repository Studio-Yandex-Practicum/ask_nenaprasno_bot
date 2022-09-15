import re
from datetime import timedelta, timezone
from typing import Optional
from urllib.parse import urlencode, urljoin

from constants.timezone import MOSCOW_TIME_OFFSET
from core.config import TRELLO_BORD_ID, URL_ASK_NENAPRASNO


def get_timezone_from_str(tz_string: Optional[str]) -> timezone:
    """Returns timezone based on user.timezone."""
    if tz_string is None:
        return timezone(timedelta(hours=MOSCOW_TIME_OFFSET))

    tz_pattern = r"UTC(?P<sign>[\+|\-])(?P<hours>\d{2}):(?P<minutes>\d{2})"
    sign, hours, minutes = re.search(tz_pattern, tz_string).groups()
    tz_delta = timedelta(hours=int(hours), minutes=int(minutes))
    return timezone(tz_delta) if sign == "+" else timezone(-tz_delta)


def build_trello_url(username_trello: str, overdue: bool = False) -> str:
    trello_filter = [f"member:{username_trello}"]
    if overdue:
        trello_filter.append("overdue:true")
    params = {"filter": ",".join(trello_filter)}

    return "/?".join((urljoin("https://trello.com/", TRELLO_BORD_ID), urlencode(params)))


def build_consultation_url(consultation_id: str) -> str:
    return urljoin(URL_ASK_NENAPRASNO, f"/consultation/redirect/{consultation_id}")
