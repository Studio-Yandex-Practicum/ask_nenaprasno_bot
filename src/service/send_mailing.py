from string import Template
from typing import Any, Optional, Union, List
import logging

from telegram.error import TelegramError
from telegram.ext import CallbackContext
from telegram import ReplyKeyboardMarkup

from src.core.send_message import send_message
from src.service.api_client_dataclasses import UserMonthStat, UserWeekStat
from src.service import ConreateAPIService


async def send_month_statistic(
    context: CallbackContext, reply_markup: Optional[ReplyKeyboardMarkup]
):
    mont_statistic_obj = await ConreateAPIService().get_month_stat()
    message = Template('')
    await start_mailing_statistic(
        context=context, template_message=message,
        statistic=mont_statistic_obj.month_stat,
        parse_mode='Markdown',
        reply_markup=reply_markup
    )


async def send_week_statistic(
    context: CallbackContext, reply_markup: Optional[ReplyKeyboardMarkup]
):
    week_statistic_obj = await ConreateAPIService().get_week_stat()
    message = Template('')
    await start_mailing_statistic(
        context=context, template_message=message,
        statistic=week_statistic_obj.week_stat,
        parse_mode='Markdown',
        reply_markup=reply_markup
    )


async def start_mailing_statistic(
    context: CallbackContext,
    template_message: Template,
    statistic: List[Union[UserMonthStat, UserWeekStat]],
    parse_mode: Any = None,
    reply_markup: Optional[ReplyKeyboardMarkup] = None
):
    for user_statistic in statistic:
        await send_message(
            context=context,
            chat_id=user_statistic.telegram_id,
            text=template_message.substitute(**user_statistic.__dict__),
            parse_mode=parse_mode,
            reply_markup=reply_markup
        )
