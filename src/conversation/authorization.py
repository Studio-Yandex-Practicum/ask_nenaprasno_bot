from urllib.parse import urljoin

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import CallbackContext, CallbackQueryHandler, CommandHandler, ConversationHandler

from constants import callback_data, states
from conversation.menu import menu_conversation
from conversation.timezone import ASK_FLAG, set_timezone_from_keyboard, timezone_conversation
from core import config
from core.send_message import edit_message, reply_message
from decorators.logger import async_error_logger
from menu_button import COMMANDS_UNAUTHORIZED, menu_button
from service.api_client import APIService
from service.api_client.models import UserData
from texts.buttons import BTN_CONSULTATION, BTN_NO, BTN_SUPPORT, BTN_YES
from texts.conversation import (
    BOT_GREETINGS_MESSAGE,
    BOT_OFFER_FILL_FORM_FOR_FUTURE_EXPERT,
    BOT_OFFER_ONLINE_CONSULTATION,
    BOT_OFFER_SEND_TELEGRAM_ID,
    BOT_QUESTON_WANT_BE_EXPERT,
    BOT_QUESTON_YOU_ARE_EXPERT,
)


@async_error_logger(name="conversation.authorization.start")
async def start(update: Update, context: CallbackContext) -> str:
    """
    Responds to the start command. The entry point to telegram bot.
    """
    user_data = await autorize(update.effective_user.id, context)
    if user_data is not None:
        await reply_message(update=update, text=BOT_GREETINGS_MESSAGE)
        context.user_data[ASK_FLAG] = True
        await set_timezone_from_keyboard(update, context)
        return states.MENU_STATE
    await menu_button(context, COMMANDS_UNAUTHORIZED)
    keyboard = [
        [
            InlineKeyboardButton(BTN_YES, callback_data=callback_data.CALLBACK_IS_EXPERT_COMMAND),
            InlineKeyboardButton(BTN_NO, callback_data=callback_data.CALLBACK_NOT_EXPERT_COMMAND),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await reply_message(update=update, text=BOT_QUESTON_YOU_ARE_EXPERT, reply_markup=reply_markup)
    return states.UNAUTHORIZED_STATE


@async_error_logger(name="conversation.authorization.not_expert_callback")
async def not_expert_callback(update: Update, context: CallbackContext) -> str:
    """
    Invites the user to become an expert.
    """
    keyboard = [
        [
            InlineKeyboardButton(BTN_YES, callback_data=callback_data.CALLBACK_REGISTER_AS_EXPERT_COMMAND),
            InlineKeyboardButton(BTN_NO, callback_data=callback_data.CALLBACK_SUPPORT_OR_CONSULT_COMMAND),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await edit_message(update=update, new_text=BOT_QUESTON_WANT_BE_EXPERT, reply_markup=reply_markup)
    return states.REGISTRATION_STATE


@async_error_logger(name="conversation.authorization.support_or_consult_callback")
async def support_or_consult_callback(update: Update, context: CallbackContext) -> int:
    """
    Offers to support the project.
    """
    keyboard = [
        [
            InlineKeyboardButton(BTN_CONSULTATION, url=config.URL_ASK_NENAPRASNO),
            InlineKeyboardButton(BTN_SUPPORT, url=urljoin(config.URL_ASK_NENAPRASNO, "/#donation")),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await edit_message(update=update, new_text=BOT_OFFER_ONLINE_CONSULTATION, reply_markup=reply_markup)
    return ConversationHandler.END


@async_error_logger(name="conversation.authorization.register_as_expert_callback")
async def register_as_expert_callback(update: Update, context: CallbackContext) -> int:
    """
    Sends a registration form to the user.
    """
    await reply_message(update=update, text=BOT_OFFER_FILL_FORM_FOR_FUTURE_EXPERT)
    return ConversationHandler.END


async def autorize(telegram_id: int, context: CallbackContext) -> UserData:
    """
    Try to authenticate telegram user on site API.
    """
    api_service = APIService()
    user_data = await api_service.authenticate_user(telegram_id=telegram_id)
    if user_data is not None:
        context.user_data["username"] = user_data.username
        context.user_data["timezone"] = user_data.timezone
        context.user_data["username_trello"] = user_data.username_trello
    return user_data


@async_error_logger(name="conversation.authorization.is_expert_callback")
async def is_expert_callback(update: Update, context: CallbackContext) -> str:
    """
    Try to authenticate telegram user on site API and write trello_id to persistence file.
    """
    telegram_id = update.effective_user.id
    user_data = await autorize(update.effective_user.id, context)
    await update.callback_query.answer()
    if user_data is None:
        message = BOT_OFFER_SEND_TELEGRAM_ID.format(telegram_id=telegram_id)
        await edit_message(update=update, new_text=message)
        return states.UNAUTHORIZED_STATE
    await edit_message(update=update, new_text=BOT_GREETINGS_MESSAGE)
    context.user_data[ASK_FLAG] = True
    await set_timezone_from_keyboard(update, context)
    return states.MENU_STATE


authorization_conversation = ConversationHandler(
    allow_reentry=True,
    persistent=True,
    name="authorization_conversation",
    entry_points=[
        CommandHandler("start", start),
    ],
    states={
        states.UNAUTHORIZED_STATE: [
            CallbackQueryHandler(is_expert_callback, pattern=callback_data.CALLBACK_IS_EXPERT_COMMAND),
            CallbackQueryHandler(not_expert_callback, pattern=callback_data.CALLBACK_NOT_EXPERT_COMMAND),
        ],
        states.REGISTRATION_STATE: [
            CallbackQueryHandler(
                register_as_expert_callback, pattern=callback_data.CALLBACK_REGISTER_AS_EXPERT_COMMAND
            ),
            CallbackQueryHandler(
                support_or_consult_callback, pattern=callback_data.CALLBACK_SUPPORT_OR_CONSULT_COMMAND
            ),
        ],
        states.MENU_STATE: [menu_conversation, timezone_conversation],
    },
    fallbacks=[],
)
