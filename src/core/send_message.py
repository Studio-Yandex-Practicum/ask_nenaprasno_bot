from string import Template
from typing import Optional, List, Union
import logging

from telegram.constants import ParseMode
from telegram.error import TelegramError
from telegram.ext import CallbackContext
from telegram import ReplyKeyboardMarkup

from src.service.api_client.models import MonthStat, WeekStat


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
        logging.exception(("The error sending the message to the chat: %s", chat_id), error)
        return False


async def send_statistics(
    context: CallbackContext,
    template_message: Template,
    template_attribute_aliases: dict,
    statistic: List[Union[MonthStat, WeekStat]],
    reply_markup: Optional[ReplyKeyboardMarkup] = None,
):
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
        message = template_message.substitute(
            {key: getattr(user_statistic, attribute)
             for key, attribute in template_attribute_aliases.items()}
        )
        await send_message(
            context=context,
            chat_id=user_statistic.telegram_id,
            text=message,
            reply_markup=reply_markup
        )
