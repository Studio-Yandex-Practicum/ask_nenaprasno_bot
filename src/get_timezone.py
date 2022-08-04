import datetime

import pytz
from telegram import Update
from telegram.ext import CallbackContext
from timezonefinder import TimezoneFinder

from service.api_client import APIService

TIME_ZONE = "UTC"


async def set_timezone(telegram_id: int, text_utc: str, context: CallbackContext):
    api = APIService()
    await api.set_user_timezone(telegram_id=telegram_id, user_time_zone=text_utc)


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
    return str(update.message.text)
