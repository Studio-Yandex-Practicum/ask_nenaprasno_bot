# pylint: disable=no-member
from collections import defaultdict
from dataclasses import dataclass
from datetime import date, datetime, timedelta, timezone
from typing import Dict, List, Optional, Tuple

from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext

from constants.callback_data import CALLBACK_DONE_BILL_COMMAND, CALLBACK_SKIP_BILL_COMMAND
from constants.timezone import MOSCOW_TIME_OFFSET
from conversation.menu import OVERDUE_TEMPLATE, format_average_user_answer_time, format_rating, make_consultations_list
from core import config
from core.send_message import send_message
from core.utils import build_consultation_url, build_trello_url, get_timezone_from_str, get_word_case, get_word_genitive
from service.api_client import APIService
from service.api_client.models import Consultation
from service.repeat_message import repeat_after_one_hour_button

REMINDER_BASE_TEMPLATE = (
    "[Открыть заявку на сайте]({site_url})\n"
    "----\n"
    "В работе **{active_consultations}** {declination_consultation}\n"
    "Истекает срок у **{expired_consultations}** {genitive_declination_consultation}\n\n"
    "[Открыть Trello]({trello_overdue_url})"
)

DUE_REMINDER_TEMPLATE = (
    "Нееееет! Срок ответа на заявку {consultation_number} истек :(\n" "Мы все очень ждем вашего ответа.\n\n"
) + REMINDER_BASE_TEMPLATE

DUE_HOUR_REMINDER_TEMPLATE = (
    "Час прошел, а наша надежда - нет :)\n" "Ответьте, пожалуйста, на заявку {consultation_number}\n\n"
) + REMINDER_BASE_TEMPLATE

PAST_REMINDER_TEMPLATE = (
    "Время и стекло 😎\n" "Заявка от {created} - **{consultation_number}**\n" "Верим и ждем.\n\n"
) + REMINDER_BASE_TEMPLATE

FORWARD_REMINDER_TEMPLATE = (
    "Пупупууу! Истекает срок ответа по заявке {consultation_number} 🔥\n"
    "У нас еще есть время, чтобы ответить человеку вовремя!\n\n"
) + REMINDER_BASE_TEMPLATE

WEEKLY_STATISTIC_TEMPLATE = (
    "Вы делали добрые дела 7 дней!\n"
    'Посмотрите, как прошла ваша неделя в *"Просто спросить"*\n'
    "Закрыто заявок - *{closed_consultations}*\n"
    "В работе *{active_consultations}* {declination_consultation} за неделю\n\n"
    "Истекает срок у *{expiring_consultations}* {genitive_declination_consultation}\n"
    "У *{expired_consultations}* {genitive_declination_expired} срок истек\n\n"
    "[Открыть Trello]({trello_url})\n\n"
    "Мы рады работать в одной команде :)\n"
    "Так держать!\n"
)

MONTHLY_STATISTIC_TEMPLATE = (
    "Это был отличный месяц!\n"
    'Посмотрите, как он прошел в *"Просто спросить"* 🔥\n\n'
    "Количество закрытых заявок - *{closed_consultations}*\n"
    "{rating}"
    "{average_user_answer_time}\n"
    "[Открыть Trello]({trello_url})\n\n"
    "Мы рады работать в одной команде :)\n"
    "Так держать!\n"
)

DATE_FORMAT = "%Y-%m-%dT%H:%M:%S.%fZ"
NATIONAL_DATE_FORMAT = "%d.%m.%Y"

service = APIService()


@dataclass(frozen=True)
class BaseConsultationData:
    """Stores structured data that is passed
    within a job to the job_queue of the bot.
    """

    consultation: Consultation
    message_template: Optional[str]

    def __get_date(self, prop: str) -> date:
        return datetime.strptime(getattr(self.consultation, prop), DATE_FORMAT).date()

    def due_date(self) -> date:
        return self.__get_date("due")

    def created_date(self) -> date:
        return self.__get_date("created")


@dataclass(frozen=True)
class DueConsultationData(BaseConsultationData):
    """Stores structured data to be passed
    right upon expiration of the due time.
    """

    message_template: str = DUE_REMINDER_TEMPLATE

    def consultation_in_valid_time_range(self) -> bool:
        return self.due_date() == datetime.utcnow().date()


@dataclass(frozen=True)
class DueHourConsultationData(BaseConsultationData):
    """Stores structured data to be passed
    one hour after expiration of the due time.
    """

    message_template: str = DUE_HOUR_REMINDER_TEMPLATE

    def consultation_in_valid_time_range(self) -> bool:
        return self.due_date() == datetime.utcnow().date()


@dataclass(frozen=True)
class PastConsultationData(BaseConsultationData):
    """Stores structured data to be passed
    for consultations expired at least one day ago.
    """

    message_template: str = PAST_REMINDER_TEMPLATE

    def consultation_in_valid_time_range(self) -> bool:
        return self.due_date() < datetime.utcnow().date()


@dataclass(frozen=True)
class ForwardConsultationData(BaseConsultationData):
    """Stores structured data to be passed
    for consultations expiring tomorrow.
    """

    message_template: str = FORWARD_REMINDER_TEMPLATE

    def consultation_in_valid_time_range(self) -> bool:
        return self.due_date() - datetime.utcnow().date() == timedelta(days=1)


async def weekly_stat_job(context: CallbackContext) -> None:
    """Collects users timezones and adds statistic-sending jobs to queue."""
    week_statistics = await service.get_week_stat()
    # микропроблема: если у пользователя не выбрана таймзона, то в сете будет None,
    # который в send_weekly_statistic_job будет интрепретирован как таймзона по-умолчанию (МСК)
    # Таким образом на МСК будет 2 джобы
    timezones = set(statistic.timezone for statistic in week_statistics)

    for tz_string in timezones:
        timezone_ = get_timezone_from_str(tz_string)
        start_time = (
            timedelta(microseconds=1)
            if timezone_ == timezone.utc
            else config.WEEKLY_STAT_TIME.replace(tzinfo=timezone_)
        )
        context.job_queue.run_once(send_weekly_statistic_job, when=start_time, data=tz_string)


async def monthly_stat_job(context: CallbackContext) -> None:
    """Collects users timezones and adds statistic-sending jobs to queue."""
    month_statistics = await service.get_month_stat()

    for statistic in month_statistics:
        if statistic.telegram_id is None:
            continue
        timezone_ = get_timezone_from_str(statistic.timezone)
        start_time = (
            timedelta(microseconds=1)
            if timezone_ == timezone.utc
            else config.MONTHLY_STAT_TIME.replace(tzinfo=timezone_)
        )
        context.job_queue.run_once(send_monthly_statistic_job, when=start_time, data=statistic)


async def send_weekly_statistic_job(context: CallbackContext) -> None:
    """Sends weekly statistics to users with specific timezone."""
    current_tz = context.job.data
    week_statistics = await service.get_week_stat()

    for statistic in filter(lambda stat: stat.telegram_id is not None and stat.timezone == current_tz, week_statistics):
        message = WEEKLY_STATISTIC_TEMPLATE.format(
            trello_url=build_trello_url(statistic.username_trello),
            **statistic.to_dict(),
            declination_consultation=get_word_case(statistic.active_consultations, "заявка", "заявки", "заявок"),
            genitive_declination_consultation=get_word_genitive(statistic.expiring_consultations, "заявки", "заявок"),
            genitive_declination_expired=get_word_genitive(statistic.expired_consultations, "заявки", "заявок"),
        )
        await send_message(
            bot=context.bot,
            chat_id=statistic.telegram_id,
            text=message,
            reply_markup=None,
        )


async def send_monthly_statistic_job(context: CallbackContext) -> None:
    """Send monthly statistic to user."""
    statistic = context.job.data
    message = MONTHLY_STATISTIC_TEMPLATE.format(
        closed_consultations=statistic.closed_consultations,
        rating=format_rating(statistic.rating),
        average_user_answer_time=format_average_user_answer_time(statistic.average_user_answer_time),
        trello_url=build_trello_url(statistic.username_trello),
    )
    await send_message(
        bot=context.bot,
        chat_id=statistic.telegram_id,
        text=message,
    )


async def monthly_bill_reminder_job(context: CallbackContext) -> None:
    """Send monthly reminder about the receipt formation during payment
    Only for self-employed users
    """
    bill_stat = await service.get_bill()
    user_list = bill_stat.telegram_ids
    for telegram_id in user_list:
        context.job_queue.run_once(daily_bill_remind_job, when=timedelta(seconds=1), user_id=telegram_id)


async def daily_bill_remind_job(context: CallbackContext) -> None:
    """Send message every day until delete job from JobQueue
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
    # Не смог понять в каком виде хранятся данные о часовом поясе юзера. Здесь надо переопределить информацию о
    # времени отправки сообщения
    # if user_utc:
    #     send_time += user_utc

    context.job_queue.run_daily(
        daily_bill_remind_job,
        time=send_time,
        user_id=job.user_id,
        name=f"send_{job.user_id}_bill_until_complete",
    )


async def get_consultations_count(telegram_id: int) -> Tuple:
    """Gets count of active and expired consultations and returns it in tuple."""
    active_cons_count = (await service.get_user_active_consultations(telegram_id=telegram_id)).active_consultations
    expired_cons_count = (await service.get_user_expired_consultations(telegram_id=telegram_id)).expired_consultations

    return active_cons_count, expired_cons_count


async def get_overdue_reminder_text(consultations: List, active_cons_count: int, expired_cons_count: int) -> str:
    """Returns overdue reminder text if user have more than one overdue consultations."""
    link_nenaprasno = make_consultations_list(
        [Consultation.to_dict(consultation.consultation) for consultation in consultations]
    )
    trello_url = build_trello_url(consultations[0].consultation.username_trello, overdue=True)

    return OVERDUE_TEMPLATE.format(
        active_consultations=active_cons_count,
        expired_consultations=expired_cons_count,
        link_nenaprasno=link_nenaprasno,
        trello_url=trello_url,
    )


def get_reminder_text(
    data: [PastConsultationData | DueConsultationData | DueHourConsultationData | ForwardConsultationData],
    active_cons_count: int,
    expired_cons_count: int,
) -> str:
    """Returns reminder text."""
    message_template = data.message_template
    consultation = data.consultation

    return message_template.format(
        consultation_id=consultation.id,
        consultation_number=consultation.number,
        created=data.created_date,
        active_consultations=active_cons_count,
        expired_consultations=expired_cons_count,
        site_url=build_consultation_url(consultation.id),
        trello_overdue_url=build_trello_url(consultation.username_trello, True),
        declination_consultation=get_word_case(active_cons_count, "заявка", "заявки", "заявок"),
        genitive_declination_consultation=get_word_genitive(expired_cons_count, "заявки", "заявок"),
    )


async def check_consultation_status_and_send_reminder(context: CallbackContext) -> None:
    """Sends reminder after check."""
    if context.job.data.consultation_in_valid_time_range():
        await send_reminder_now(context)


async def send_reminder_now(context: CallbackContext) -> None:
    """Sends reminder without check."""
    job_data = context.job.data

    consultation = job_data.consultation
    telegram_id = consultation.telegram_id
    consultation_count = await get_consultations_count(telegram_id)
    text = get_reminder_text(job_data, *consultation_count)

    await send_message(
        bot=context.bot,
        chat_id=telegram_id,
        text=text,
    )


async def send_reminder_overdue(context: CallbackContext) -> None:
    """Send overdue-consultation reminder"""
    telegram_id, consultations = context.job.data
    active_cons_count, expired_cons_count = await get_consultations_count(telegram_id)

    if len(consultations) == 1:
        message = get_reminder_text(
            consultations[0],
            active_cons_count,
            expired_cons_count,
        )
    else:
        message = await get_overdue_reminder_text(consultations, active_cons_count, expired_cons_count)

    await send_message(bot=context.bot, chat_id=telegram_id, text=message)


async def daily_overdue_consulations_reminder_job(context: CallbackContext, overdue: Dict) -> None:
    """Creates tasks to send reminders for consultations expired at least one day ago."""
    for telegram_id, consultations in overdue.items():
        if consultations:
            # Send reminder job for every doctor
            context.job_queue.run_once(
                send_reminder_overdue,
                when=timedelta(seconds=1),
                data=(telegram_id, consultations),
            )


async def daily_consulations_duedate_is_today_reminder_job(context: CallbackContext) -> None:
    """Adds a reminder job to the bot's job queue according to the scenario:
    - the due date is today
    """
    now = datetime.utcnow()
    consultations = await service.get_daily_consultations()

    for consultation in consultations:
        due_time = datetime.strptime(consultation.due, DATE_FORMAT)

        if due_time.date() == now.date():
            # Bot will check consultation status and remind at due_time if consultations is still active
            context.job_queue.run_once(
                check_consultation_status_and_send_reminder, when=due_time, data=DueConsultationData(consultation)
            )
            # Bot will check consultation status and remind one hour after due time if consultation is still active
            context.job_queue.run_once(
                check_consultation_status_and_send_reminder,
                when=due_time + timedelta(hours=1),
                data=DueHourConsultationData(consultation),
            )


async def daily_consulations_reminder_job(context: CallbackContext) -> None:
    """Adds a reminder job to the bot's job queue according
    to one of the following scenarios:
    - the due date is tomorrow;
    - the due date has just expired;
    - the due date expired one hour ago.
    """
    now = datetime.utcnow()
    default_timezone = timezone(timedelta(hours=MOSCOW_TIME_OFFSET))
    consultations = await service.get_daily_consultations()
    overdue = defaultdict(list)

    for consultation in consultations:
        # Check every consultation
        user_timezone = context.bot_data.get(int(consultation.telegram_id), default_timezone)
        due_time = datetime.strptime(consultation.due, DATE_FORMAT)
        user_time = datetime.now(tz=user_timezone)

        # Important. This job starts every hour at 0 minutes 0 seconds, so we need to check only hour
        if user_time.hour == config.DAILY_CONSULTATIONS_REMINDER_TIME.hour:
            # Check consultation in right timezone
            if due_time.date() < now.today():
                # Group overdue consultations by doctor
                overdue[consultation.telegram_id].append(PastConsultationData(consultation))
            elif due_time.date() - now.date() == timedelta(days=1):
                # Due date is tomorrow, send one reminder per consultationsnow
                context.job_queue.run_once(
                    send_reminder_now,
                    when=timedelta(seconds=1),
                    data=ForwardConsultationData(consultation),
                )

    if overdue:
        await daily_overdue_consulations_reminder_job(context, overdue)
