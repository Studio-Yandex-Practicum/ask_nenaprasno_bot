import zoneinfo

from telegram import KeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove, Update
from telegram.ext import CallbackContext
from timezonefinder import TimezoneFinder

# from api_client import set_user_timezone


RHETORICAL_TEXT = ("Напишу свою таймзону сам", "Отправить свою геолокацию для автоматической настройки часового пояса")


async def get_timezone(update: Update, context: CallbackContext):
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
    if update.message.location is not None:
        user_timezone = TimezoneFinder().timezone_at(
            lng=update.message.location.longitude, lat=update.message.location.latitude
        )
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=f'Установлен часовой пояс "{user_timezone}"',
            reply_markup=ReplyKeyboardRemove(),
        )
        # set_user_timezone(
        #     telegram_id=update.effective_chat.id,
        #     user_timezone=user_timezone
        # )
    elif update.message.text:
        try:
            zoneinfo.ZoneInfo(str(update.message.text))
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=f"Установлен часовой пояс {update.message.text}",
                reply_markup=ReplyKeyboardRemove(),
            )
            # set_user_timezone(
            #     telegram_id=update.effective_chat.id,
            #     user_timezone=user_timezone
            # )
        except zoneinfo.ZoneInfoNotFoundError:
            text = str(update.message.text)
            if text not in RHETORICAL_TEXT or set("/").isdisjoint(text):
                await context.bot.send_message(
                    chat_id=update.effective_chat.id,
                    text=(
                        f'Часового пояса "{text}" нет. Попробуйте'
                        " написать другой или передайте геолокацию для его автоматического"
                        " определения."
                    ),
                )
