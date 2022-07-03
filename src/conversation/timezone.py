from telegram import KeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove, Update
from telegram.ext import CallbackContext, CommandHandler, ContextTypes, MessageHandler, filters

from constants import commands, states
from core.send_message import send_message
from get_timezone import get_timezone_from_location, get_timezone_from_text_message

TIME_ZONE = "UTC"


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
    return states.TIMEZONE_STATE


async def check_timezone(update: Update, context: ContextTypes.DEFAULT_TYPE, timezone):
    """
    Sends a message after a successful timezone installation.
    """
    if timezone is None:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="Не удалось определить часовой пояс. Пожалуйста, введите его вручную. Например: UTC+03:00",
        )
        return states.TIMEZONE_STATE
    await send_message(
        context=context,
        chat_id=update.effective_chat.id,
        text="Вы настроили часовой пояс, теперь уведомления будут приходить в удобное время",
        reply_markup=ReplyKeyboardRemove(),
    )
    return states.BASE_STATE


async def get_timezone_from_location_callback(update: Update, context: CallbackContext):
    """
    Sets timezone by geolocation.
    """
    timezone = await get_timezone_from_location(update, context)
    state = await check_timezone(update, context, timezone)
    return state


async def get_timezone_from_text_message_callback(update: Update, context: CallbackContext):
    """
    Sets timezone based on a text message from the user.
    """
    text = str(update.message.text)
    if text == "Напишу свою таймзону сам":
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="Введите таймзону UTC. Например: UTC+03:00",
        )
        return states.TIMEZONE_STATE
    timezone = await get_timezone_from_text_message(update, context)
    if timezone:
        await send_message(
            context=context, chat_id=update.effective_chat.id, text=("вы установили таймзону " + str(timezone))
        )

    state = await check_timezone(update, context, timezone)
    return state


states_timezone_conversation_dict = {
    states.TIMEZONE_STATE: [
        MessageHandler(filters.LOCATION, get_timezone_from_location_callback),
        MessageHandler(filters.TEXT & ~filters.COMMAND, get_timezone_from_text_message_callback),
    ],
}

timezone_command_handler = CommandHandler(commands.GET_TIMEZONE, get_timezone)
