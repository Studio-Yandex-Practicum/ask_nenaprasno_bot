import datetime
import re
from typing import Optional

import pytz
from telegram import Update
from telegram.ext import CallbackContext
from timezonefinder import TimezoneFinder

from constants.timezone import DEFAULT_TIMEZONE, MOSCOW_TIME_OFFSET, TIME_ZONE
from service.api_client import APIService

api = APIService()


def get_timezone_from_str(tz_string: Optional[str]) -> Optional[datetime.timezone]:
    """Returns datetime.timezone based on string in format UTC+00:00."""
    if tz_string is None:
        return datetime.timezone(datetime.timedelta(hours=MOSCOW_TIME_OFFSET))

    tz_pattern = r"(?i)(UTC)?(?P<sign>[-+]?)(?P<hours>(0?[1-9])|(1[0-2]))(:0{1,2})?$"
    tz_result = re.search(tz_pattern, tz_string)
    if tz_result is not None:
        tz_delta = datetime.timedelta(
            hours=int(tz_result.group("hours")),
        )
        if tz_result.group("sign") in ("+", ""):
            return datetime.timezone(tz_delta)
        return datetime.timezone(-tz_delta)
    return None


async def set_timezone(telegram_id: int, text_utc: str, context: CallbackContext) -> None:
    await api.set_user_timezone(telegram_id=telegram_id, user_time_zone=text_utc)
    context.bot_data.update({telegram_id: get_timezone_from_str(text_utc)})


async def get_timezone_from_location(update: Update, context: CallbackContext):
    """
    Sets timezone by geolocation.
    Return None if error, any else (string with timezone will be best).
    """
    user_timezone = TimezoneFinder().timezone_at(
        lng=update.message.location.longitude, lat=update.message.location.latitude
    )
    if user_timezone is not None:
        time_zone = pytz.timezone(user_timezone)
        utc_time = datetime.datetime.utcnow()
        utc = float(time_zone.utcoffset(utc_time).total_seconds() / 3600)
        hours, minutes = divmod(utc * 60, 60)
        utc = f"{hours:+03.0f}:{minutes:02.0f}"
        text_utc = TIME_ZONE + utc
        await set_timezone(update.effective_chat.id, text_utc, context)
        return text_utc
    return None


async def get_timezone_from_text_message(update: Update, context: CallbackContext):
    """
    Sets timezone based on a text message from the user.
    Return None if error, any else (string with timezone will be best).
    """
    timezone = get_timezone_from_str(update.message.text)
    if timezone is not None:
        text_utc = str(timezone)
        await set_timezone(update.effective_chat.id, text_utc, context)
        return text_utc


async def get_user_timezone(telegram_id: int, context: CallbackContext) -> datetime.timezone:
    """
    Return user timezone.

    If user doesn't set timezone - returns default timezone.
    """
    user_tz = context.bot_data.get(telegram_id, None)

    if user_tz is None:
        user_data = await api.authenticate_user(telegram_id)
        user_tz = get_timezone_from_str(user_data.timezone if hasattr(user_data, "timezone") else DEFAULT_TIMEZONE)
        context.bot_data.update({telegram_id: user_tz})

    return user_tz
