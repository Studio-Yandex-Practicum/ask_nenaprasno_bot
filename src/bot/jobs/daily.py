from collections import defaultdict
from datetime import datetime, timedelta
from typing import Dict, List, Union

from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext

from bot.constants import callback_data
from bot.conversation import menu as mn
from bot.decorators.logger import async_job_logger
from bot.jobs import models, templates
from bot.services.timezone_service import get_user_timezone
from bot.utils.repeat_message import repeat_after_one_hour_button
from core.config import settings
from core.logger import logger
from core.send_message import send_message
from core.utils import build_consultation_url, build_trello_url, get_word_case, get_word_genitive
from service.api_client import APIService
from service.api_client.models import Consultation

__api = APIService()


@async_job_logger
async def daily_bill_remind_job(context: CallbackContext) -> None:
    """Send message every day until delete job from JobQueue."""
    logger.debug("Running daily_bill_remind_job")
    job = context.job
    message = "Вы активно работали весь месяц! Не забудьте отправить чек нашему кейс-менеджеру"
    menu = InlineKeyboardMarkup(
        [
            [InlineKeyboardButton("✅ Уже отправил(а)", callback_data=callback_data.CALLBACK_DONE_BILL_COMMAND)],
            [repeat_after_one_hour_button],
            [InlineKeyboardButton("🕑 Скоро отправлю", callback_data=callback_data.CALLBACK_SKIP_BILL_COMMAND)],
        ]
    )
    await send_message(context.bot, job.chat_id, message, menu)


def get_overdue_reminder_text(
    consultations: List, active_consultations_count: int, expired_consultations_count: int, **kwargs
) -> str:
    """Returns overdue reminder text if user have more than one overdue consultations."""
    link_nenaprasno = mn.make_consultations_list(
        [Consultation.to_dict(consultation.consultation) for consultation in consultations]  # pylint: disable=E1101
    )
    trello_url = build_trello_url(consultations[0].consultation.username_trello, overdue=True)

    return mn.OVERDUE_TEMPLATE.format(
        active_consultations=active_consultations_count,
        expired_consultations=expired_consultations_count,
        link_nenaprasno=link_nenaprasno,
        trello_url=trello_url,
    )


def get_reminder_text(
    data: Union[
        models.PastConsultationData,
        models.DueConsultationData,
        models.DueHourConsultationData,
        models.ForwardConsultationData,
    ],
    active_consultations_count: int,
    expired_consultations_count: int,
    **kwargs,
) -> str:
    """Returns reminder text."""
    message_template = data.message_template
    consultation = data.consultation
    return message_template.format(
        consultation_id=consultation.id,
        consultation_number=consultation.number,
        created=data.created_date,
        active_consultations=active_consultations_count,
        expired_consultations=expired_consultations_count,
        site_url=build_consultation_url(consultation.id),
        trello_overdue_url=build_trello_url(consultation.username_trello, True),
        declination_consultation=get_word_case(active_consultations_count, "заявка", "заявки", "заявок"),
        genitive_declination_consultation=get_word_genitive(expired_consultations_count, "заявки", "заявок"),
    )


@async_job_logger
async def check_consultation_status_and_send_reminder(context: CallbackContext) -> None:
    """Sends reminder after check."""
    consultation = context.job.data
    if consultation.in_valid_time_range():
        await send_reminder_now(context)


@async_job_logger
async def send_reminder_now(context: CallbackContext) -> None:
    """Sends reminder without check."""
    job_data = context.job.data

    consultation = job_data.consultation
    telegram_id = consultation.telegram_id
    consultations_count = await __api.get_consultations_count(telegram_id)
    text = get_reminder_text(job_data, **consultations_count)

    await send_message(context.bot, telegram_id, text)


@async_job_logger
async def send_reminder_overdue(context: CallbackContext) -> None:
    """Send overdue-consultation reminder"""
    telegram_id, consultations = context.job.data
    consultations_count = await __api.get_consultations_count(telegram_id)

    if len(consultations) == 1:
        message = get_reminder_text(consultations[0], **consultations_count)
    else:
        message = get_overdue_reminder_text(consultations, **consultations_count)

    await send_message(context.bot, telegram_id, message)


@async_job_logger
async def daily_overdue_consulations_reminder_job(context: CallbackContext, overdue: Dict) -> None:
    """Creates tasks to send reminders for consultations expired at least one day ago."""
    logger.debug("Running daily_overdue_consulations_reminder_job")
    for telegram_id, consultations in overdue.items():
        if consultations:
            # Send reminder job for every doctor
            context.job_queue.run_once(
                send_reminder_overdue,
                when=timedelta(seconds=1),
                data=(telegram_id, consultations),
            )
            logger.debug(
                "Add %s to job queue. Start in 1 second for user %s", send_reminder_overdue.__name__, telegram_id
            )


@async_job_logger
async def daily_consulations_duedate_is_today_reminder_job(context: CallbackContext) -> None:
    """Adds a reminder job to the bot's job queue according to the scenario:
    - the due date is today
    """
    logger.debug("Running daily_consulations_duedate_is_today_reminder_job")
    now = datetime.utcnow()
    consultations = await __api.get_daily_consultations()

    for consultation in consultations:
        due_time = datetime.strptime(consultation.due, templates.DATE_FORMAT)

        if due_time.date() == now.date():
            # Bot will check consultation status and remind at due_time if consultations is still active
            context.job_queue.run_once(
                check_consultation_status_and_send_reminder,
                when=due_time,
                data=models.DueConsultationData(consultation),
            )
            logger.debug(
                "Add %s to job queue. Start at %s for user %s",
                check_consultation_status_and_send_reminder.__name__,
                due_time,
                consultation.telegram_id,
            )
            # Bot will check consultation status and remind one hour after due time if consultation is still active
            context.job_queue.run_once(
                check_consultation_status_and_send_reminder,
                when=due_time + timedelta(hours=1),
                data=models.DueHourConsultationData(consultation),
            )
            logger.debug(
                "Add %s to job queue. Start at %s for user %s",
                check_consultation_status_and_send_reminder.__name__,
                due_time + timedelta(hours=1),
                consultation.telegram_id,
            )


@async_job_logger
async def daily_consulations_reminder_job(context: CallbackContext) -> None:
    """Adds a reminder job to the bot's job queue according
    to one of the following scenarios:
    - the due date is tomorrow;
    - the due date has just expired;
    - the due date expired one hour ago.
    """
    logger.debug("Running daily_consultations_reminder_job")
    now = datetime.utcnow()
    consultations = await __api.get_daily_consultations()
    overdue = defaultdict(list)

    for consultation in consultations:
        # Check every consultation
        if consultation.telegram_id is None:
            logger.debug("DCRJ: consultation.telegram_id: %s", consultation.telegram_id)
            continue
        user_timezone = await get_user_timezone(int(consultation.telegram_id), context)
        due_time = datetime.strptime(consultation.due, templates.DATE_FORMAT)
        user_time = datetime.now(tz=user_timezone)
        logger.debug(
            "DCRJ: user_timezone: %s, due_time: %s, user_time: %s, telegram_id: %s",
            user_timezone,
            due_time,
            user_time,
            consultation.telegram_id,
        )

        # Important. This job starts every hour at 0 minutes 0 seconds, so we need to check only hour
        if user_time.hour == settings.daily_consultations_reminder_time.hour:
            # Check consultation in right timezone
            if due_time.date() < now.date():
                # Group overdue consultations by doctor
                overdue[consultation.telegram_id].append(models.PastConsultationData(consultation))
            elif due_time.date() - now.date() == timedelta(days=1):
                # Due date is tomorrow, send one reminder per consultations now
                context.job_queue.run_once(
                    send_reminder_now,
                    when=timedelta(seconds=1),
                    data=models.ForwardConsultationData(consultation),
                )
                logger.debug(
                    "Add %s to job queue. Start in 1 second for user %s",
                    send_reminder_now.__name__,
                    consultation.telegram_id,
                )

    if overdue:
        await daily_overdue_consulations_reminder_job(context, overdue)
