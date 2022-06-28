import logging
from string import Template

from telegram.constants import ParseMode
from telegram.ext import CallbackContext

from src.core.send_message import send_statistics
from src.service.send_mailing import send_month_statistic, send_week_statistic
from src.service import ConreateAPIService


async def weekly_stat_job(context: CallbackContext) -> None:
    """
    Send weekly statistics on the number of requests in the work
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
    await send_statistics(
        context=context, template_message=message,
        statistic=week_statistic_obj.week_stat,
        parse_mode=ParseMode.MARKDOWN,
    )


async def monthly_receipt_reminder_job(context: CallbackContext) -> None:
    """
    Send monthly reminder about the receipt formation during payment
    Only for self-employed users
    """


async def monthly_stat_job(context: CallbackContext) -> None:
    """
    Send monthly statistics on the number of successfully
    closed requests.
    Only if the user had requests
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
    await send_statistics(
        context=context, template_message=message,
        statistic=mont_statistic_obj.month_stat,
        parse_mode=ParseMode.MARKDOWN,
    )

