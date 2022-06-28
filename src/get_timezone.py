import datetime

import pytz
from telegram import KeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove, Update
from telegram.ext import CallbackContext, CommandHandler, MessageHandler, filters
from timezonefinder import TimezoneFinder

from service.api_client_fake import FakeAPIService


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


async def set_timezone(telegram_id: int, utc: int, context: CallbackContext):
    await context.bot.send_message(
        chat_id=telegram_id,
        text=f"Установлен часовой пояс для UTC {utc}",
        reply_markup=ReplyKeyboardRemove(),
    )
    api = FakeAPIService()
    await api.set_user_timezone(telegram_id=telegram_id, user_timezone=utc)


async def get_timezone_from_location(update: Update, context: CallbackContext) -> None:
    user_timezone = TimezoneFinder().timezone_at(
        lng=update.message.location.longitude, lat=update.message.location.latitude
    )
    if user_timezone is None:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=("Не удалось определить часовой пояс. Пожалуйста, введите его вручную. Например: UTC+3"),
        )
    else:
        time_zone = pytz.timezone(user_timezone)
        utc_time = datetime.datetime.utcnow()
        utc = int(time_zone.utcoffset(utc_time).total_seconds() // 3600)
        await set_timezone(update.effective_chat.id, utc, context)


async def get_timezone_from_text_message(update: Update, context: CallbackContext) -> None:
    text = str(update.message.text)
    if text == "Напишу свою таймзону сам":
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="Введите таймзону. Например: UTC+3",
        )
    else:
        text = text.replace(" ", "")
        try:
            utc = int(list(filter(None, text.split("UTC")))[0])
            await set_timezone(update.effective_chat.id, utc, context)
        except ValueError:
            if set("/").isdisjoint(text):
                await context.bot.send_message(
                    chat_id=update.effective_chat.id,
                    text=(
                        f'Не смогли установить часовой пояс для "{text}". Попробуйте'
                        " написать ещё раз. Например: : UTC+3\nИли передайте геолокацию для его автоматического"
                        " определения."
                    ),
                )


get_timezone_command_handler = CommandHandler("get_timezone", get_timezone)
get_timezone_from_location_handler = MessageHandler(filters.LOCATION, get_timezone_from_location)
get_timezone_from_text_handler = MessageHandler(filters.TEXT, get_timezone_from_text_message)
