from string import Template
from typing import Optional

from telegram.ext import CallbackContext
from telegram import ReplyKeyboardMarkup
from telegram.constants import ParseMode

from src.service import ConreateAPIService
from src.core.send_message import sending_statistics


async def send_month_statistic(
    context: CallbackContext,
    reply_markup: Optional[ReplyKeyboardMarkup] = None,
):
    """
    Sends monthly statistics to users using a template message.
    :param context: CallbackContext
    :param reply_markup: ReplyKeyboardMarkup | None
    """
    mont_statistic_obj = await ConreateAPIService().get_month_stat()
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
    await sending_statistics(
        context=context, template_message=message,
        statistic=mont_statistic_obj.month_stat,
        parse_mode=ParseMode.MARKDOWN,
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
    week_statistic_obj = await ConreateAPIService().get_week_stat()
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
    await sending_statistics(
        context=context, template_message=message,
        statistic=week_statistic_obj.week_stat,
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=reply_markup
    )
    return True
