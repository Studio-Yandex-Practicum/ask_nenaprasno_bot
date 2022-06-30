from string import Template

from telegram.ext import CallbackContext

from src.core.send_message import send_statistics
from src.service.api_client import APIService


async def weekly_stat_job(context: CallbackContext) -> None:
    """
    Send weekly statistics on the number of requests in the work
    """
    week_statistics = await APIService().get_week_stat()
    template_message = Template(
        'Вы делали добрые дела 7 дней!\n'
        'Посмотрите, как прошла ваша неделя  в *""Просто спросить""*\n'
        'Закрыто заявок - *$tickets_closed*\n'
        'В работе *$tickets_in_work* заявок  за неделю\n\n'
        'Истекает срок у *$tickets_expiring заявок*\n'
        'У *$tickets_expired* заявок срок истек\n\n'
        'Открыть [Trello](https://trello.com)\n\n'
        'Мы рады работать в одной команде :)\n'
        '*Так держать!*'
    )
    alias_dict = dict(
        tickets_closed='last_week_user_tickets_closed',
        tickets_in_work='last_week_user_tickets_in_work',
        tickets_expiring='last_week_user_tickets_expiring',
        tickets_expired='last_week_user_tickets_expired'
    )
    await send_statistics(
        context, template_message, alias_dict,
        week_statistics,
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
    mont_statistics = await APIService().get_month_stat()
    template_message = Template(
        'Это был отличный месяц!\n'
        'Посмотрите, как он прошел в *""Просто спросить""* 🔥\n\n'
        'Количество закрытых заявок - *$tickets_closed*\n'
        'Рейтинг - *$rating*\n'
        'Среднее время ответа - *$ticket_resolve_avg_time*\n\n'
        'Открыть [Trello](https://trello.com)\n\n'
        'Мы рады работать в одной команде :)\n'
        '*Так держать!*'
    )
    alias_dict = dict(
        tickets_closed='user_tickets_closed',
        rating='user_rating',
        ticket_resolve_avg_time='user_ticket_resolve_avg_time',
    )
    await send_statistics(
        context, template_message, alias_dict,
        mont_statistics,
    )
