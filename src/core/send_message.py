import logging
from typing import Optional

from telegram import Bot, InlineKeyboardMarkup, ReplyKeyboardMarkup, Update
from telegram.constants import ParseMode
from telegram.error import Forbidden, TelegramError

from core.logger import logger


async def send_message(
    bot: Bot,
    chat_id: int,
    text: str,
    reply_markup: Optional[ReplyKeyboardMarkup | InlineKeyboardMarkup] = None,
) -> bool:
    """Send simple text message."""
    try:
        await bot.send_message(chat_id, text, ParseMode.MARKDOWN, reply_markup=reply_markup)
        return True
    except Forbidden:
        logger.warning("Forbidden: bot was blocked by the user: %s", chat_id)
    except TelegramError:
        if logger.level == logging.DEBUG:
            logging.exception("The error sending the message to the chat: %s", chat_id)
        else:
            logging.warning("The error sending the message to the chat: %s", chat_id)
    return False


async def edit_message(
    update: Update,
    new_text: str,
    reply_markup: Optional[ReplyKeyboardMarkup | InlineKeyboardMarkup] = None,
) -> bool:
    """Edit text message."""
    try:
        await update.callback_query.edit_message_text(new_text, ParseMode.MARKDOWN, reply_markup=reply_markup)
        return True
    except TelegramError:
        logger.exception("The error editing the message to the chat: %d", update.effective_chat.id)
        return False


async def reply_message(
    update: Update,
    text: str,
    reply_markup: Optional[ReplyKeyboardMarkup | InlineKeyboardMarkup] = None,
) -> bool:
    """Reply on the message."""
    try:
        message = update.callback_query.message if update.message is None else update.message
        await message.reply_markdown(text, reply_markup=reply_markup)
        return True
    except TelegramError:
        logger.exception("The error reply on the message to the chat: %d", update.effective_chat.id)
        return False
