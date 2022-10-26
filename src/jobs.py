# pylint: disable=no-member
from collections import defaultdict
from dataclasses import dataclass
from datetime import date, datetime, timedelta
from typing import Dict, List, Optional

from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext

from constants.callback_data import CALLBACK_DONE_BILL_COMMAND, CALLBACK_SKIP_BILL_COMMAND
from constants.jobs import USER_BILL_REMINDER_TEMPLATE
from conversation.menu import OVERDUE_TEMPLATE, format_average_user_answer_time, format_rating, make_consultations_list
from core import config
from core.send_message import send_message
from core.utils import build_consultation_url, build_trello_url, get_word_case, get_word_genitive
from get_timezone import get_timezone_from_str, get_user_timezone
from service.api_client import APIService
from service.api_client.models import Consultation
from service.repeat_message import repeat_after_one_hour_button
from texts.bot import (
    BILL_REMINDER_TEXT,
    DUE_HOUR_REMINDER_TEMPLATE,
    DUE_REMINDER_TEMPLATE,
    FORWARD_REMINDER_TEMPLATE,
    MONTHLY_STATISTIC_TEMPLATE,
    PAST_REMINDER_TEMPLATE,
    WEEKLY_STATISTIC_TEMPLATE,
)
from texts.buttons import BTN_BILL_SENT, BTN_BILL_SOON
from texts.common import PLURAL_CONSULTATION, PLURAL_CONSULTATION_NOT_SINGLE

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

    def in_valid_time_range(self) -> bool:
        return self.due_date() == datetime.utcnow().date()


@dataclass(frozen=True)
class DueHourConsultationData(BaseConsultationData):
    """Stores structured data to be passed
    one hour after expiration of the due time.
    """

    message_template: str = DUE_HOUR_REMINDER_TEMPLATE

    def in_valid_time_range(self) -> bool:
        return self.due_date() == datetime.utcnow().date()


@dataclass(frozen=True)
class PastConsultationData(BaseConsultationData):
    """Stores structured data to be passed
    for consultations expired at least one day ago.
    """

    message_template: str = PAST_REMINDER_TEMPLATE

    def in_valid_time_range(self) -> bool:
        return self.due_date() < datetime.utcnow().date()


@dataclass(frozen=True)
class ForwardConsultationData(BaseConsultationData):
    """Stores structured data to be passed
    for consultations expiring tomorrow.
    """

    message_template: str = FORWARD_REMINDER_TEMPLATE

    def in_valid_time_range(self) -> bool:
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
        start_time = config.WEEKLY_STAT_TIME.replace(tzinfo=timezone_)
        context.job_queue.run_once(send_weekly_statistic_job, when=start_time, data=tz_string)


async def monthly_stat_job(context: CallbackContext) -> None:
    """Collects users timezones and adds statistic-sending jobs to queue."""
    month_statistics = await service.get_month_stat()

    for statistic in month_statistics:
        if statistic.telegram_id is None:
            continue
        timezone_ = get_timezone_from_str(statistic.timezone)
        start_time = config.MONTHLY_STAT_TIME.replace(tzinfo=timezone_)
        context.job_queue.run_once(send_monthly_statistic_job, when=start_time, data=statistic)


async def send_weekly_statistic_job(context: CallbackContext) -> None:
    """Sends weekly statistics to users with specific timezone."""
    current_tz = context.job.data
    week_statistics = await service.get_week_stat()

    for statistic in filter(lambda stat: stat.telegram_id is not None and stat.timezone == current_tz, week_statistics):
        message = WEEKLY_STATISTIC_TEMPLATE.format(
            trello_url=build_trello_url(statistic.username_trello),
            **statistic.to_dict(),
            declination_consultation=get_word_case(statistic.active_consultations, *PLURAL_CONSULTATION),
            genitive_declination_consultation=get_word_genitive(
                statistic.expiring_consultations, *PLURAL_CONSULTATION_NOT_SINGLE
            ),
            genitive_declination_expired=get_word_genitive(
                statistic.expired_consultations, *PLURAL_CONSULTATION_NOT_SINGLE
            ),
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
    """
    Send monthly reminder about the receipt formation during payment.

    Only for self-employed users.
    """
    bill_stat = await service.get_bill()
    if bill_stat is None:
        return

    user_ids = bill_stat.telegram_ids
    for telegram_id in user_ids:
        user_tz = await get_user_timezone(int(telegram_id), context)
        job_name = USER_BILL_REMINDER_TEMPLATE.format(telegram_id=telegram_id)

        current_jobs = context.job_queue.get_jobs_by_name(job_name)
        for job in current_jobs:
            job.schedule_removal()

        context.job_queue.run_daily(
            daily_bill_remind_job,
            time=config.MONTHLY_RECEIPT_REMINDER_TIME.replace(tzinfo=user_tz),
            name=job_name,
            chat_id=telegram_id,
        )


async def daily_bill_remind_job(context: CallbackContext) -> None:
    """Send message every day until delete job from JobQueue."""
    job = context.job
    menu = InlineKeyboardMarkup(
        [
            [InlineKeyboardButton(BTN_BILL_SENT, callback_data=CALLBACK_DONE_BILL_COMMAND)],
            [repeat_after_one_hour_button],
            [InlineKeyboardButton(BTN_BILL_SOON, callback_data=CALLBACK_SKIP_BILL_COMMAND)],
        ]
    )
    await send_message(context.bot, job.chat_id, BILL_REMINDER_TEXT, menu)


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
        trello_url=build_trello_url(consultation.username_trello, True),
        declination_consultation=get_word_case(active_cons_count, *PLURAL_CONSULTATION),
        genitive_declination_consultation=get_word_genitive(expired_cons_count, *PLURAL_CONSULTATION_NOT_SINGLE),
    )


async def check_consultation_status_and_send_reminder(context: CallbackContext) -> None:
    """Sends reminder after check."""
    consultation = context.job.data
    if consultation.in_valid_time_range():
        await send_reminder_now(context)


async def send_reminder_now(context: CallbackContext) -> None:
    """Sends reminder without check."""
    job_data = context.job.data

    consultation = job_data.consultation
    telegram_id = consultation.telegram_id
    consultation_count = await service.get_consultations_count(telegram_id)
    text = get_reminder_text(job_data, *consultation_count)

    await send_message(
        bot=context.bot,
        chat_id=telegram_id,
        text=text,
    )


async def send_reminder_overdue(context: CallbackContext) -> None:
    """Send overdue-consultation reminder"""
    telegram_id, consultations = context.job.data
    active_cons_count, expired_cons_count = await service.get_consultations_count(telegram_id)

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
    consultations = await service.get_daily_consultations()
    overdue = defaultdict(list)

    for consultation in consultations:
        # Check every consultation
        user_timezone = await get_user_timezone(int(consultation.telegram_id), context)
        due_time = datetime.strptime(consultation.due, DATE_FORMAT)
        user_time = datetime.now(tz=user_timezone)

        # Important. This job starts every hour at 0 minutes 0 seconds, so we need to check only hour
        if user_time.hour == config.DAILY_CONSULTATIONS_REMINDER_TIME.hour:
            # Check consultation in right timezone
            if due_time.date() < now.date():
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
