import zoneinfo

from telegram import KeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove, Update
from telegram.ext import CallbackContext, CommandHandler, MessageHandler, filters
from timezonefinder import TimezoneFinder

from service.api_client_real import RealAPIService

RHETORICAL_TEXT = ("Напишу свою таймзону сам", "Отправить свою геолокацию для автоматической настройки часового пояса")


async def get_timezone(update: Update, context: CallbackContext):
    keyboard = [
        [KeyboardButton(RHETORICAL_TEXT[1], request_location=True)],
        [KeyboardButton(RHETORICAL_TEXT[0])],
    ]
    markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True)

    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Для начала, давайте настроим часовой пояс, чтобы вы получали уведомления в удобное время",
        reply_markup=markup,
    )


async def get_timezone_from_location(update: Update, context: CallbackContext):
    if update.message.location is not None:
        user_timezone = TimezoneFinder().timezone_at(
            lng=update.message.location.longitude, lat=update.message.location.latitude
        )
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=f'Установлен часовой пояс "{user_timezone}"',
            reply_markup=ReplyKeyboardRemove(),
        )
        api = RealAPIService()
        await api.set_user_timezone(telegram_id=update.effective_chat.id, user_timezone=user_timezone)
    elif update.message.text:
        text = str(update.message.text)
        try:
            zoneinfo.ZoneInfo(text)
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=f"Установлен часовой пояс {update.message.text}",
                reply_markup=ReplyKeyboardRemove(),
            )
            api = RealAPIService()
            await api.set_user_timezone(telegram_id=update.effective_chat.id, user_timezone=user_timezone)
        except zoneinfo.ZoneInfoNotFoundError:
            if text not in RHETORICAL_TEXT and set("/").isdisjoint(text):
                await context.bot.send_message(
                    chat_id=update.effective_chat.id,
                    text=(
                        f'Часового пояса "{text}" нет. Попробуйте'
                        " написать другой или передайте геолокацию для его автоматического"
                        " определения."
                    ),
                )


get_timezone_command_handler = CommandHandler("get_timezone", get_timezone)
get_timezone_from_location_handler = MessageHandler(filters.TEXT | filters.LOCATION, get_timezone_from_location)
