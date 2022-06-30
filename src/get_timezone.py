import datetime

import pytz
from telegram import KeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove, Update
from telegram.ext import CallbackContext, CommandHandler, MessageHandler, filters
from timezonefinder import TimezoneFinder

from service.api_client import APIService

TIME_ZONE = "UTC"


async def get_timezone(update: Update, context: CallbackContext) -> None:
    keyboard = [
        [
            KeyboardButton(
                "Отправить свою геолокацию для автоматической настройки часового пояса", request_location=True
            )
        ],
        [KeyboardButton("Напишу свою таймзону сам")],
    ]
    markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True)

    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Для начала, давайте настроим часовой пояс, чтобы вы получали уведомления в удобное время",
        reply_markup=markup,
    )


async def set_timezone(telegram_id: int, text_utc: str, context: CallbackContext):
    await context.bot.send_message(
        chat_id=telegram_id,
        text=f"Установлен часовой пояс для {text_utc}",
        reply_markup=ReplyKeyboardRemove(),
    )
    api = APIService()
    await api.set_user_timezone(telegram_id=telegram_id, user_time_zone=text_utc)


async def get_timezone_from_location(update: Update, context: CallbackContext) -> None:
    user_timezone = TimezoneFinder().timezone_at(
        lng=update.message.location.longitude, lat=update.message.location.latitude
    )
    if user_timezone is None:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=("Не удалось определить часовой пояс. Пожалуйста, введите его вручную. Например: UTC+03:00"),
        )
    else:
        time_zone = pytz.timezone(user_timezone)
        utc_time = datetime.datetime.utcnow()
        utc = float(time_zone.utcoffset(utc_time).total_seconds() / 3600)
        hours, minutes = divmod(utc * 60, 60)
        utc = f"{hours:+03.0f}:{minutes:02.0f}"
        text_utc = TIME_ZONE + utc
        await set_timezone(update.effective_chat.id, text_utc, context)


async def get_timezone_from_text_message(update: Update, context: CallbackContext) -> None:
    text = str(update.message.text)
    if text == "Напишу свою таймзону сам":
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="Введите таймзону UTC. Например: UTC+03:00",
        )
    else:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="вы установили таймзону X",
        )


get_timezone_command_handler = CommandHandler("get_timezone", get_timezone)
get_timezone_from_location_handler = MessageHandler(filters.LOCATION, get_timezone_from_location)
get_timezone_from_text_handler = MessageHandler(filters.TEXT, get_timezone_from_text_message)
