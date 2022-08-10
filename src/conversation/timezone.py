from telegram import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove,
    Update,
)
from telegram.ext import CallbackContext, ContextTypes, MessageHandler, filters

from constants import callback_data, states
from core.config import URL_SERVICE_RULES
from core.send_message import reply_message
from decorators.logger import async_error_logger
from get_timezone import get_timezone_from_location, get_timezone_from_text_message

TIME_ZONE = "UTC"


@async_error_logger(name="conversation.timezone.get_timezone")
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
    message = "Для начала, давайте настроим часовой пояс, чтобы вы получали уведомления в удобное время"
    await reply_message(update=update, text=message, reply_markup=markup)
    return states.TIMEZONE_STATE


@async_error_logger(name="conversation.timezone.check_timezone")
async def check_timezone(update: Update, context: ContextTypes.DEFAULT_TYPE, timezone):
    """
    Sends a message after a successful timezone installation.
    Return state for ConversationHandler.
    """
    if timezone is None:
        await reply_message(
            update=update,
            text=(
                "Не удалось определить часовой пояс. "
                "Пожалуйста, введите его вручную. Например: UTC+03:00, UTC-03:00, utc3:0 и даже 3:0"
            ),
        )
        return states.TIMEZONE_STATE
    buttons_after_timezone = [
        [
            InlineKeyboardButton(
                text="Статистика за месяц", callback_data=callback_data.CALLBACK_STATISTIC_MONTH_COMMAND
            ),
        ],
        [InlineKeyboardButton(text="В работе", callback_data=callback_data.CALLBACK_ACTUAL_REQUESTS_COMMAND)],
        [InlineKeyboardButton(text="🔥 Cроки горят", callback_data=callback_data.CALLBACK_OVERDUE_REQUESTS_COMMAND)],
        [
            InlineKeyboardButton(
                text="Правила сервиса",
                url=URL_SERVICE_RULES,
            )
        ],
    ]
    await reply_message(
        update=update,
        text=f"Вы настроили часовой пояс *{timezone}*, теперь уведомления будут приходить в удобное время.",
        reply_markup=ReplyKeyboardRemove(),
    )
    reply_markup = InlineKeyboardMarkup(buttons_after_timezone)
    await reply_message(
        update=update,
        text="А еще с помощью меня вы можете узнать про:",
        reply_markup=reply_markup,
    )
    return states.MENU_STATE


@async_error_logger(name="conversation.timezone.get_timezone_from_location_callback")
async def get_timezone_from_location_callback(update: Update, context: CallbackContext):
    """
    Sets timezone by geolocation.
    """
    timezone = await get_timezone_from_location(update, context)
    return await check_timezone(update, context, timezone)


@async_error_logger(name="conversation.timezone.get_timezone_from_text_message_callback")
async def get_timezone_from_text_message_callback(update: Update, context: CallbackContext):
    """
    Sets timezone based on a text message from the user.
    """
    text = str(update.message.text)
    if text == "Напишу свою таймзону сам":
        await reply_message(
            update=update, text="Введите таймзону UTC. Например: UTC+03:00, UTC-03:00, utc3:0 и даже 3:0"
        )
        return states.TIMEZONE_STATE
    timezone = await get_timezone_from_text_message(update, context)
    return await check_timezone(update, context, timezone)


states_timezone_conversation_dict = {
    states.TIMEZONE_STATE: [
        MessageHandler(filters.LOCATION, get_timezone_from_location_callback),
        MessageHandler(filters.TEXT & ~filters.COMMAND, get_timezone_from_text_message_callback),
    ],
}
