from string import Template
import logging

from telegram.ext import CallbackContext

from src.core.send_message import send_message
from src.service import ConreateAPIService


async def weekly_stat_job(context: CallbackContext) -> None:
    """
    Send weekly statistics on the number of requests in the work
    """
    week_statistic_obj = await ConreateAPIService().get_week_stat()
    pre_message = Template(
        'Вы делали добрые дела 7 дней!\n'
        'Посмотрите, как прошла ваша неделя  в *""Просто спросить""*\n'
        'Закрыто заявок - *$tickets_closed*\n'
        'В работе *$tikets_in_work* заявок  за неделю\n\n'
        'Истекает срок у *$tickets_expiring заявок*\n'
        'У *$tickets_expired* заявок срок истек\n\n'
        'Открыть [Trello](https://trello.com)\n\n'
        'Мы рады работать в одной команде :)\n'
        '*Так держать!*'
    )
    for user_statistic in week_statistic_obj.week_stat:
        if user_statistic.username not in context.bot_data['username_to_id']:
            logging.warning(
                f'User with username {user_statistic.username} '
                f'not found in bot data. Maybe user not run bot '
                f'or not authenticated in bot')
            continue
        chat_id = context.bot_data['username_to_id'][user_statistic.username]
        message = pre_message.substitute(
            tickets_closed=user_statistic.last_week_user_tickets_closed,
            tikets_in_work=user_statistic.last_week_user_tikets_in_work,
            tickets_expiring=user_statistic.last_week_user_tickets_expiring,
            tickets_expired=user_statistic.last_week_user_tickets_expired,
        )
        await send_message(
            context=context,
            chat_id=chat_id,
            text=message,
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
    pre_message = Template(
        'Это был отличный месяц!\n'
        'Посмотрите, как он прошел в *""Просто спросить""* 🔥\n\n'
        'Количество закрытых заявок - *$tickets_closed*\n'
        'Рейтинг - *$rating*\n'
        'Среднее время ответа - *$ticket_resolve_avg_time*\n\n'
        'Открыть [Trello](https://trello.com)\n\n'
        'Мы рады работать в одной команде :)\n'
        '*Так держать!*'
    )
    for user_statistic in mont_statistic_obj.month_stat:
        if user_statistic.username not in context.bot_data['username_to_id']:
            logging.warning(
                f'User with username {user_statistic.username} '
                f'not found in bot data. Maybe user not run bot '
                f'or not authenticated in bot')
            continue
        chat_id = context.bot_data['username_to_id'][user_statistic.username]
        message = pre_message.substitute(
            tickets_closed=user_statistic.user_tickets_closed,
            rating=user_statistic.user_rating,
            ticket_resolve_avg_time=user_statistic.user_ticket_resolve_avg_time,
        )
        await send_message(
            context=context,
            chat_id=chat_id,
            text=message,
        )
