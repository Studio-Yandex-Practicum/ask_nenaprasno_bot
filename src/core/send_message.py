from typing import Optional
import logging

from telegram.constants import ParseMode
from telegram.error import TelegramError
from telegram.ext import CallbackContext
from telegram import ReplyKeyboardMarkup


async def send_message(
    context: CallbackContext,
    chat_id: int,
    text: str,
    parse_mode: str = ParseMode.MARKDOWN,
    reply_markup: Optional[ReplyKeyboardMarkup] = None
) -> bool:
    """
    Send simple text message.
    :param context: CallbackContext
    :param chat_id: int
    :param parse_mode: Any
    :param text: str
    :param reply_markup: ReplyKeyboardMarkup | None
    """
    try:
        await context.bot.send_message(
            chat_id=chat_id,
            text=text,
            parse_mode=parse_mode,
            reply_markup=reply_markup,
        )
        return True

    except TelegramError as error:
        logging.exception(
            f'The error sending the message to the chat: {chat_id}',
            error
        )
        return False
