from telegram import KeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove, Update
from telegram.ext import CallbackContext, ContextTypes, MessageHandler, filters

from constants import states
from core.send_message import send_message
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
    await send_message(context=context, chat_id=update.effective_chat.id, text=message, reply_markup=markup)
    return states.TIMEZONE_STATE


@async_error_logger(name="conversation.timezone.check_timezone")
async def check_timezone(update: Update, context: ContextTypes.DEFAULT_TYPE, timezone):
    """
    Sends a message after a successful timezone installation.
    Return state for ConversationHandler.
    """
    chat_id = update.effective_chat.id
    if timezone is None:
        await send_message(
            context=context,
            chat_id=chat_id,
            text="Не удалось определить часовой пояс. Пожалуйста, введите его вручную. Например: UTC+03:00",
        )
        return states.TIMEZONE_STATE
    await send_message(context=context, chat_id=chat_id, text=f"Установлен часовой пояс для {timezone}")
    await send_message(
        context=context,
        chat_id=chat_id,
        text="Вы настроили часовой пояс, теперь уведомления будут приходить в удобное время",
        reply_markup=ReplyKeyboardRemove(),
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
    chat_id = update.effective_chat.id
    if text == "Напишу свою таймзону сам":
        await send_message(context=context, chat_id=chat_id, text="Введите таймзону UTC. Например: UTC+03:00")
        return states.TIMEZONE_STATE
    timezone = await get_timezone_from_text_message(update, context)
    return await check_timezone(update, context, timezone)


states_timezone_conversation_dict = {
    states.TIMEZONE_STATE: [
        MessageHandler(filters.LOCATION, get_timezone_from_location_callback),
        MessageHandler(filters.TEXT & ~filters.COMMAND, get_timezone_from_text_message_callback),
    ],
}
