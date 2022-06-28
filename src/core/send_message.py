from typing import Any, Optional, List, Union
import logging
from string import Template

from telegram.error import TelegramError
from telegram.ext import CallbackContext
from telegram import ReplyKeyboardMarkup

from src.service.api_client_dataclasses import UserMonthStat, UserWeekStat


async def send_message(
    context: CallbackContext,
    chat_id: int,
    text: str,
    parse_mode: Any = None,
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


async def sending_statistics(
    context: CallbackContext,
    template_message: Template,
    statistic: List[Union[UserMonthStat, UserWeekStat]],
    parse_mode: Any = None,
    reply_markup: Optional[ReplyKeyboardMarkup] = None,
):
    """
    Start mailing message with statistics.
    :param context: CallbackContext
    :param template_message: Template
    :param statistic: List[Union[UserMonthStat, UserWeekStat]]
    :param parse_mode: Any = None
    :param reply_markup: ReplyKeyboardMarkup | None
    """
    for user_statistic in statistic:
        await send_message(
            context=context,
            chat_id=user_statistic.telegram_id,
            text=template_message.substitute(**user_statistic.__dict__),
            parse_mode=parse_mode,
            reply_markup=reply_markup
        )
