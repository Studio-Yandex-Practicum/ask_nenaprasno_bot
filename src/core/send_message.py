import logging

from telegram import ReplyKeyboardMarkup
from telegram.error import TelegramError
from telegram.ext import CallbackContext

from src.constants.error_messages import TELEGRAM_ERROR_MESSAGE


async def send_message(
    context: CallbackContext, chat_id: int, text: str, reply_markup: ReplyKeyboardMarkup | None = None
) -> bool:
    """
    Send simple text message.
    :param context: CallbackContext
    :param chat_id: int
    :param text: str
    :param reply_mark_up: ReplyKeyboardMarkup | None
    """
    try:
        await context.bot.send_message(chat_id=chat_id, text=text, reply_markup=reply_markup)
        return True

    except TelegramError as error:
        logging.exception((TELEGRAM_ERROR_MESSAGE, chat_id), error)
        return False
