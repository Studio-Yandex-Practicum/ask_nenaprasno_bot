from datetime import date, datetime, timedelta
from enum import Enum
from string import Template

from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext

from constants.callback_data import CALLBACK_DONE_BILL_COMMAND, CALLBACK_SKIP_BILL_COMMAND
from core import config
from core.send_message import send_message, send_statistics
from service.api_client import APIService
from service.repeat_message import repeat_after_one_hour_button

REMINDER_BASE_TEMPLATE = (
    "Открыть заявку на сайте (https://ask-nnyp.klbrtest.ru"
    "/consultation/redirect/{consultation_id})\n"
    "----\n"
    "В работе **{active_consultations}** заявок\n"
    "Истекает срок у **{expired_consultations}** заявок\n\n"
    "Открыть Trello (https://trello.com/{trello_id}/"
    "?filter=member:{trello_name}/?filter=overdue:true)"
)

HOURLY_REMINDER_TEMPLATE = (
    "Час прошел, а наша надежда - нет :)\n" "Ответьте, пожалуйста, на заявку {consultation_id}\n\n"
) + REMINDER_BASE_TEMPLATE

DAILY_REMINDER_TEMPLATE = (
    "Время и стекло 😎\n" "Заявка - {consultation_id}\n" "Верим и ждем.\n\n"
) + REMINDER_BASE_TEMPLATE

FORWARD_REMINDER_TEMPLATE = (
    "Пупупууу! Истекает срок ответа по заявке {consultation_id} 🔥\n"
    "У нас еще есть время, чтобы ответить человеку вовремя!\n\n"
) + REMINDER_BASE_TEMPLATE

DATE_FORMAT = "%Y-%m-%dT%H:%M:%S.%fZ"

service = APIService()


class DueStatus(Enum):
    """Defines due status of a consultation:
    - EXPIRED: due date at least one day ago;
    - TODAY: due date is today;
    - TOMORROW: due day is tomorrow.
    """

    EXPIRED = 1
    TODAY = 2
    TOMORROW = 3


async def weekly_stat_job(context: CallbackContext) -> None:
    """
    Send weekly statistics on the number of requests in the work
    """
    week_statistics = await service.get_week_stat()
    template_message = Template(
        "Вы делали добрые дела 7 дней!\n"
        'Посмотрите, как прошла ваша неделя  в *"Просто спросить"*\n'
        "Закрыто заявок - *$closed_consultations*\n"
        "В работе *$active_consultations* заявок  за неделю\n\n"
        "Истекает срок у *$expiring_consultations* заявок\n"
        "У *$expired_consultations* заявок срок истек\n\n"
        f"[Открыть Trello](https://trello.com/{config.TRELLO_BORD_ID})\n\n"
    )
    alias_dict = dict(
        closed_consultations="closed_consultations",
        active_consultations="active_consultations",
        expiring_consultations="expiring_consultations",
        expired_consultations="expired_consultations",
    )
    await send_statistics(
        context=context,
        template_message=template_message,
        template_attribute_aliases=alias_dict,
        statistic=week_statistics,
        reply_markup=InlineKeyboardMarkup([[repeat_after_one_hour_button]]),
    )


async def monthly_stat_job(context: CallbackContext) -> None:
    """
    Send monthly statistics on the number of successfully
    closed requests.

    Only if the user had requests.
    """
    month_statistics = await service.get_month_stat()
    template_message = Template(
        "Это был отличный месяц!\n"
        'Посмотрите, как он прошел в *"Просто спросить"* 🔥\n\n'
        "Количество закрытых заявок - *$closed_consultations*\n"
        "Рейтинг - *$rating*\n"
        "Среднее время ответа - *$average_user_answer_time*\n\n"
        f"[Открыть Trello](https://trello.com/{config.TRELLO_BORD_ID})\n\n"
    )
    alias_dict = dict(
        closed_consultations="closed_consultations",
        rating="rating",
        average_user_answer_time="average_user_answer_time",
    )
    await send_statistics(
        context=context,
        template_message=template_message,
        template_attribute_aliases=alias_dict,
        statistic=month_statistics,
    )


async def monthly_bill_reminder_job(context: CallbackContext) -> None:
    """
    Send monthly reminder about the receipt formation during payment
    Only for self-employed users
    """
    bill_stat = await service.get_bill()
    user_list = bill_stat.telegram_ids
    for telegram_id in user_list:
        context.job_queue.run_once(daily_bill_remind_job, when=timedelta(seconds=1), user_id=telegram_id)


async def daily_bill_remind_job(context: CallbackContext) -> None:
    """
    Send message every day until delete job from JobQueue
    :param context:
    :return:
    """
    job = context.job
    message = "Вам необходимо сформировать чек"
    bill_done_button = InlineKeyboardButton(text="✅ Уже отправил(а)", callback_data=CALLBACK_DONE_BILL_COMMAND)
    bill_skip_button = InlineKeyboardButton(text="🕑 Скоро отправлю", callback_data=CALLBACK_SKIP_BILL_COMMAND)
    menu = InlineKeyboardMarkup([[repeat_after_one_hour_button], [bill_done_button], [bill_skip_button]])
    await send_message(chat_id=job.user_id, text=message, reply_markup=menu, bot=context.bot)
    send_time = config.MONTHLY_RECEIPT_REMINDER_TIME
    # user_utc = context.user_data.get("UTC")
    # Не смог понять, в каком виде хранятся данные о часовом поясе юзера. Здесь надо переопределить информацию о
    # времени отправки сообщения
    # if user_utc:
    #     send_time += user_utc

    context.job_queue.run_daily(
        daily_bill_remind_job,
        time=send_time,
        user_id=job.user_id,
        name=f"send_{job.user_id}_bill_until_complete",
    )


async def check_consultation(consultation_id: int, due_status: DueStatus) -> bool:
    """Checks if consulation status is still valid."""
    consultation = await service.get_consultation(consultation_id)
    if consultation is None or consultation.due is None:
        return False

    due_time = datetime.strptime(consultation.due, DATE_FORMAT)
    now = datetime.utcnow()
    if due_status == DueStatus.TODAY:
        return due_time.date() == now.date()
    if due_status == DueStatus.EXPIRED:
        return due_time.date() < date.today()
    if due_status == DueStatus.TOMORROW:
        return due_time.date() - now.date() == timedelta(days=1)
    return False


async def send_reminder(context: CallbackContext) -> None:
    """Sends reminder to the user according to the message tmeplate.
    Prior to that, check if the consultation is still relevant."""
    consultation, message_template, due_status = context.job.data
    if await check_consultation(consultation.id, due_status):
        telegram_id = consultation.telegram_id
        active_cons = await service.get_user_active_consultations(telegram_id)
        expired_cons = await service.get_user_expired_consultations(telegram_id)

        message = message_template.format(
            consultation_id=consultation.id,
            active_consultations=active_cons.active_consultations,
            expired_consultations=expired_cons.expired_consultations,
            trello_id=config.TRELLO_BORD_ID,
            trello_name=consultation.username_trello,
        )
        await send_message(bot=context.bot, chat_id=telegram_id, text=message)


async def daily_consulations_reminder_job(context: CallbackContext) -> None:
    """Adds a reminder job to the bot's job queue according
    to one of the following scenarios:
    - the due date is tomorrow;
    - the due date has expired by one hour;
    - the due date expired at least one day ago.
    """
    now = datetime.utcnow()
    consultations = await service.get_daily_consultations()
    for consultation in consultations:
        due_time = datetime.strptime(consultation.due, DATE_FORMAT)
        if due_time.date() == now.date():
            message_template = HOURLY_REMINDER_TEMPLATE
            when_ = due_time + timedelta(hours=1)
            due_status = DueStatus.TODAY
        elif due_time.date() < date.today():
            message_template = DAILY_REMINDER_TEMPLATE
            when_ = datetime.time(config.DAILY_CONSULTATIONS_REMINDER_TIME)
            due_status = DueStatus.EXPIRED
        elif due_time.date() - now.date() == timedelta(days=1):
            message_template = FORWARD_REMINDER_TEMPLATE
            when_ = datetime.time(config.DAILY_CONSULTATIONS_REMINDER_TIME)
            due_status = DueStatus.TOMORROW
        else:
            continue

        context.job_queue.run_once(
            send_reminder,
            when=when_,
            data=(consultation, message_template, due_status),
        )
