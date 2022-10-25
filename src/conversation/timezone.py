from telegram import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove,
    Update,
)
from telegram.ext import (
    CallbackContext,
    CallbackQueryHandler,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    filters,
)

from constants import callback_data, states
from constants.timezone import DEFAULT_TIMEZONE
from core.config import URL_SERVICE_RULES
from core.send_message import reply_message
from decorators.logger import async_error_logger
from get_timezone import get_timezone_from_location, get_timezone_from_text_message, set_timezone
from menu_button import COMMANDS, menu_button
from texts import (
    BTN_GEOLOCATION,
    BTN_IN_PROGRESS,
    BTN_MONTH_STAT,
    BTN_OVERDUE,
    BTN_RULES,
    BTN_TIMEZONE_BY_LOCATION_OR_MANUAL,
    BTN_TIMEZONE_DEFAULT,
    MENU_HELP__,
    TIMEZONE_FAIL_MESSAGE,
    TIMEZONE_MESSAGE,
    TIMEZONE_START,
    TIMEZONE_SUCCESS_MESSAGE,
)

ASK_FLAG = "ask_flag"


@async_error_logger(name="conversation.timezone.get_timezone")
async def get_timezone(update: Update, context: CallbackContext) -> str:
    """
    Requests a timezone from the user.
    """
    keyboard = [
        [KeyboardButton(BTN_GEOLOCATION, request_location=True)],
    ]
    markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True)
    await reply_message(update=update, text=TIMEZONE_MESSAGE, reply_markup=markup)
    return states.TIMEZONE_STATE


@async_error_logger(name="conversation.timezone.check_timezone")
async def check_timezone(update: Update, context: ContextTypes.DEFAULT_TYPE, timezone: str) -> str:
    """
    Sends a message after a successful timezone installation.
    Return state for ConversationHandler.
    """
    if timezone is None:
        await reply_message(
            update=update,
            text=TIMEZONE_FAIL_MESSAGE,
        )
        return states.TIMEZONE_STATE

    if not context.user_data.get(ASK_FLAG):
        await reply_message(
            update=update,
            text=TIMEZONE_SUCCESS_MESSAGE.format(timezone=timezone),
            reply_markup=ReplyKeyboardRemove(),
        )
        return states.MENU_STATE

    buttons_after_timezone = [
        [
            InlineKeyboardButton(text=BTN_MONTH_STAT, callback_data=callback_data.CALLBACK_STATISTIC_MONTH_COMMAND),
        ],
        [InlineKeyboardButton(text=BTN_IN_PROGRESS, callback_data=callback_data.CALLBACK_ACTUAL_REQUESTS_COMMAND)],
        [InlineKeyboardButton(text=BTN_OVERDUE, callback_data=callback_data.CALLBACK_OVERDUE_REQUESTS_COMMAND)],
        [
            InlineKeyboardButton(
                text=BTN_RULES,
                url=URL_SERVICE_RULES,
            )
        ],
    ]
    reply_markup = InlineKeyboardMarkup(buttons_after_timezone)
    await reply_message(
        update=update,
        text=TIMEZONE_SUCCESS_MESSAGE.format(timezone=timezone),
        reply_markup=ReplyKeyboardRemove(),
    )
    await reply_message(
        update=update,
        text=MENU_HELP__,
        reply_markup=reply_markup,
    )
    del context.user_data[ASK_FLAG]
    return states.MENU_STATE


@async_error_logger(name="conversation.timezone.get_timezone_from_location_callback")
async def get_timezone_from_location_callback(update: Update, context: CallbackContext) -> str:
    """
    Sets timezone by geolocation.
    """
    timezone = await get_timezone_from_location(update, context)
    return await check_timezone(update, context, timezone)


@async_error_logger(name="conversation.timezone.get_timezone_from_text_message_callback")
async def get_timezone_from_text_message_callback(update: Update, context: CallbackContext) -> str:
    """
    Sets timezone based on a text message from the user.
    """
    timezone = await get_timezone_from_text_message(update, context)
    return await check_timezone(update, context, timezone)


async def set_default_timezone(update: Update, context: CallbackContext) -> str:
    """
    Sets default timezone (Moscow).
    """
    timezone = DEFAULT_TIMEZONE
    await set_timezone(update.effective_chat.id, timezone, context)
    return await check_timezone(update, context, timezone)


@async_error_logger(name="conversation.set_timezone_from_keyboard")
async def set_timezone_from_keyboard(update: Update, context: CallbackContext) -> str:
    """
    Сalls the timezone settings buttons for the authorized user.
    """
    keyboard = [
        [
            InlineKeyboardButton(
                BTN_TIMEZONE_DEFAULT,
                callback_data=callback_data.CALLBACK_SET_DEFAULT_TIMEZONE,
            ),
        ],
        [
            InlineKeyboardButton(BTN_TIMEZONE_BY_LOCATION_OR_MANUAL, callback_data=callback_data.CALLBACK_SET_TIMEZONE),
        ],
    ]
    await menu_button(context, COMMANDS)
    await reply_message(update, text=TIMEZONE_START, reply_markup=InlineKeyboardMarkup(keyboard))
    return states.MENU_STATE


timezone_conversation = ConversationHandler(
    allow_reentry=True,
    persistent=True,
    name="timezone_conversation",
    entry_points=[
        CallbackQueryHandler(get_timezone, pattern=callback_data.CALLBACK_SET_TIMEZONE),
        CallbackQueryHandler(set_default_timezone, pattern=callback_data.CALLBACK_SET_DEFAULT_TIMEZONE),
        CallbackQueryHandler(set_timezone_from_keyboard, pattern=callback_data.CALLBACK_CONFIGURATE_TIMEZONE_COMMAND),
    ],
    states={
        states.TIMEZONE_STATE: [
            MessageHandler(filters.LOCATION, get_timezone_from_location_callback),
            MessageHandler(filters.TEXT & ~filters.COMMAND, get_timezone_from_text_message_callback),
        ],
    },
    fallbacks=[],
    map_to_parent={states.MENU_STATE: states.MENU_STATE},
)
