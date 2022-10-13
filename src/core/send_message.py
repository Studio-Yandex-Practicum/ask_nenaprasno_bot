import logging
from string import Template
from typing import List, Optional

from telegram import Bot, InlineKeyboardMarkup, ReplyKeyboardMarkup, Update
from telegram.constants import ParseMode
from telegram.error import Forbidden, TelegramError
from telegram.ext import CallbackContext

from core.logger import logger
from service.api_client.models import MonthStat, WeekStat


async def send_message(
    bot: Bot,
    chat_id: int,
    text: str,
    reply_markup: Optional[ReplyKeyboardMarkup | InlineKeyboardMarkup] = None,
) -> bool:
    """Send simple text message."""
    try:
        await bot.send_message(chat_id, text, ParseMode.MARKDOWN_V2, reply_markup=reply_markup)
        return True
    except Forbidden:
        logger.warning("Forbidden: bot was blocked by the user: %s", chat_id)
    except TelegramError:
        logging.exception("The error sending the message to the chat: %s", chat_id)
    return False


async def edit_message(
    update: Update,
    new_text: str,
    reply_markup: Optional[ReplyKeyboardMarkup | InlineKeyboardMarkup] = None,
) -> bool:
    """Edit text message."""
    try:
        await update.callback_query.edit_message_text(new_text, ParseMode.MARKDOWN_V2, reply_markup=reply_markup)
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


# is useless now
async def send_statistics(
    context: CallbackContext,
    template_message: Template,
    template_attribute_aliases: dict,
    statistic: List[MonthStat | WeekStat],
    reply_markup: Optional[ReplyKeyboardMarkup | InlineKeyboardMarkup] = None,
) -> None:
    """
    Start mailing message with statistics.
    :param context: CallbackContext
    :param template_message: Template
    :param template_attribute_aliases: dict in this dictionary,
        the keys are the names of attributes in the message
        template and the keys are the names of attributes in
        the data object.
    :param statistic: List[Union[UserMonthStat, UserWeekStat]]
    :param reply_markup: ReplyKeyboardMarkup | None
    """
    for user_statistic in statistic:
        if user_statistic.telegram_id:
            message = template_message.substitute(
                {key: getattr(user_statistic, attribute) for key, attribute in template_attribute_aliases.items()}
            )
            await send_message(
                bot=context.bot, chat_id=user_statistic.telegram_id, text=message, reply_markup=reply_markup
            )
