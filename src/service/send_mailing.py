from string import Template
from typing import Any, Optional, Union, List
import logging

from telegram.ext import CallbackContext
from telegram import ReplyKeyboardMarkup

from src.core.send_message import send_message
from src.service.api_client_dataclasses import UserMonthStat, UserWeekStat
from src.service import ConreateAPIService


async def send_month_statistic(
    context: CallbackContext,
    reply_markup: Optional[ReplyKeyboardMarkup] = None,
):
    """
    Sends monthly statistics to users using a template message.
    :param context: CallbackContext
    :param reply_markup: ReplyKeyboardMarkup | None
    """
    try:
        mont_statistic_obj = await ConreateAPIService().get_month_stat()
    except Exception as error:
        logging.exception(
            'Error when trying to request month statistics',
            error
        )
        return False
    message = Template(
        'Это был отличный месяц!\n'
        'Посмотрите, как он прошел в *""Просто спросить""* 🔥\n\n'
        'Количество закрытых заявок - *$user_tickets_closed*\n'
        'Рейтинг - *$user_rating*\n'
        'Среднее время ответа - *$user_ticket_resolve_avg_time*\n\n'
        'Открыть [Trello](https://trello.com)\n\n'
        'Мы рады работать в одной команде :)\n'
        '*Так держать!*'
    )
    await start_mailing_statistic(
        context=context, template_message=message,
        statistic=mont_statistic_obj.month_stat,
        parse_mode='Markdown',
        reply_markup=reply_markup
    )
    return True


async def send_week_statistic(
    context: CallbackContext,
    reply_markup: Optional[ReplyKeyboardMarkup] = None,
):
    """
    Sends weekly statistics to users using a template message.
    :param context: CallbackContext
    :param reply_markup: ReplyKeyboardMarkup | None
    """
    try:
        week_statistic_obj = await ConreateAPIService().get_week_stat()
    except Exception as error:
        logging.exception(
            'Error when trying to request weekly statistics',
            error
        )
        return False
    message = Template(
        'Вы делали добрые дела 7 дней!\n'
        'Посмотрите, как прошла ваша неделя  в *""Просто спросить""*\n'
        'Закрыто заявок - *$last_week_user_tickets_closed*\n'
        'В работе *$last_week_user_tikets_in_work* заявок  за неделю\n\n'
        'Истекает срок у *$last_week_user_tickets_expiring заявок*\n'
        'У *$last_week_user_tickets_expired* заявок срок истек\n\n'
        'Открыть [Trello](https://trello.com)\n\n'
        'Мы рады работать в одной команде :)\n'
        '*Так держать!*'
    )
    await start_mailing_statistic(
        context=context, template_message=message,
        statistic=week_statistic_obj.week_stat,
        parse_mode='Markdown',
        reply_markup=reply_markup
    )
    return True


async def start_mailing_statistic(
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