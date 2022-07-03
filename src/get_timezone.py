from telegram import KeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove, Update
from telegram.ext import CallbackContext

from service.api_client import APIService


async def set_timezone(telegram_id: int, text_utc: str, context: CallbackContext):
    await context.bot.send_message(
        chat_id=telegram_id,
        text=f"Установлен часовой пояс для {text_utc}",
        reply_markup=ReplyKeyboardRemove(),
    )
    api = APIService()
    await api.set_user_timezone(telegram_id=telegram_id, user_time_zone=text_utc)


async def get_timezone(update: Update, context: CallbackContext):
    """
    Requests a timezone from the user.
    """
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
