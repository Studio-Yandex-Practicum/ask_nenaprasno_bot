from collections import defaultdict
from dataclasses import dataclass
from datetime import date, datetime, timedelta
from typing import Dict, List, Optional

from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext

from bot.constants import callback_data
from bot.constants.jobs import USER_BILL_REMINDER_TEMPLATE
from bot.conversation import menu as mn
from bot.decorators.logger import async_job_logger
from bot.service.repeat_message import repeat_after_one_hour_button
from bot.timezone_service import get_timezone_from_str, get_user_timezone
from core.config import settings
from core.logger import logger
from core.send_message import send_message
from core.utils import build_consultation_url, build_trello_url, get_word_case, get_word_genitive
from service.api_client import APIService
from service.api_client.models import Consultation

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


@async_job_logger
async def weekly_stat_job(context: CallbackContext) -> None:
    """Collects users timezones and adds statistic-sending jobs to queue."""
    logger.debug("Running weekly_stat_job")
    week_statistics = await service.get_week_stat()
    # микропроблема: если у пользователя не выбрана таймзона, то в сете будет None,
    # который в send_weekly_statistic_job будет интрепретирован как таймзона по-умолчанию (МСК)
    # Таким образом на МСК будет 2 джобы
    timezones = set(statistic.timezone for statistic in week_statistics)

    for tz_string in timezones:
        timezone_ = get_timezone_from_str(tz_string)
        start_time = settings.weekly_stat_time.replace(tzinfo=timezone_)
        context.job_queue.run_once(send_weekly_statistic_job, when=start_time, data=tz_string)
        logger.debug("Add %s to job queue. Start at %s", send_weekly_statistic_job.__name__, start_time)


@async_job_logger
async def monthly_stat_job(context: CallbackContext) -> None:
    """Collects users timezones and adds statistic-sending jobs to queue."""
    logger.debug("Running monthly_stat_job")
    month_statistics = await service.get_month_stat()

    for statistic in month_statistics:
        if statistic.telegram_id is None:
            continue
        timezone_ = get_timezone_from_str(statistic.timezone)
        start_time = settings.monthly_stat_time.replace(tzinfo=timezone_)
        context.job_queue.run_once(send_monthly_statistic_job, when=start_time, data=statistic)
        logger.debug(
            "Add %s to job queue. Start at %s for user %s",
            send_monthly_statistic_job.__name__,
            start_time,
            statistic.telegram_id,
        )


@async_job_logger
async def send_weekly_statistic_job(context: CallbackContext) -> None:
    """Sends weekly statistics to users with specific timezone."""
    logger.debug("Running send_weekly_statistic_job")
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


@async_job_logger
async def send_monthly_statistic_job(context: CallbackContext) -> None:
    """Send monthly statistic to user."""
    logger.debug("Running send_monthly_statistic_job")
    statistic = context.job.data
    message = MONTHLY_STATISTIC_TEMPLATE.format(
        closed_consultations=statistic.closed_consultations,
        rating=mn.format_rating(statistic.rating),
        average_user_answer_time=mn.format_average_user_answer_time(statistic.average_user_answer_time),
        trello_url=build_trello_url(statistic.username_trello),
    )
    await send_message(
        bot=context.bot,
        chat_id=statistic.telegram_id,
        text=message,
    )


@async_job_logger
async def monthly_bill_reminder_job(context: CallbackContext) -> None:
    """
    Send monthly reminder about the receipt formation during payment.

    Only for self-employed users.
    """
    logger.debug("Running monthly_bill_reminder_job")
    bill_stat = await service.get_bill()
    if bill_stat is None:
        logger.debug("Monthly bill reminder job: no bills to send")
        return

    user_ids = bill_stat.telegram_ids
    for telegram_id in user_ids:
        user_tz = await get_user_timezone(int(telegram_id), context)
        start_time = settings.monthly_receipt_reminder_time.replace(tzinfo=user_tz)
        job_name = USER_BILL_REMINDER_TEMPLATE.format(telegram_id=telegram_id)

        current_jobs = context.job_queue.get_jobs_by_name(job_name)
        for job in current_jobs:
            job.schedule_removal()
            logger.debug("Remove %s from queue", job.name)

        context.job_queue.run_daily(
            daily_bill_remind_job,
            time=start_time,
            name=job_name,
            chat_id=telegram_id,
        )
        logger.debug(
            "Add %s to job queue. Start at %s for user %s", daily_bill_remind_job.__name__, start_time, telegram_id
        )


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


async def get_overdue_reminder_text(
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
    data: [PastConsultationData | DueConsultationData | DueHourConsultationData | ForwardConsultationData],
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
    consultations_count = await service.get_consultations_count(telegram_id)
    text = get_reminder_text(job_data, **consultations_count)

    await send_message(context.bot, telegram_id, text)


@async_job_logger
async def send_reminder_overdue(context: CallbackContext) -> None:
    """Send overdue-consultation reminder"""
    telegram_id, consultations = context.job.data
    consultations_count = await service.get_consultations_count(telegram_id)

    if len(consultations) == 1:
        message = get_reminder_text(consultations[0], **consultations_count)
    else:
        message = await get_overdue_reminder_text(consultations, **consultations_count)

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
    consultations = await service.get_daily_consultations()

    for consultation in consultations:
        due_time = datetime.strptime(consultation.due, DATE_FORMAT)

        if due_time.date() == now.date():
            # Bot will check consultation status and remind at due_time if consultations is still active
            context.job_queue.run_once(
                check_consultation_status_and_send_reminder, when=due_time, data=DueConsultationData(consultation)
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
                data=DueHourConsultationData(consultation),
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
    logger.debug("Running daily_consulations_reminder_job")
    now = datetime.utcnow()
    consultations = await service.get_daily_consultations()
    overdue = defaultdict(list)

    for consultation in consultations:
        # Check every consultation
        user_timezone = await get_user_timezone(int(consultation.telegram_id), context)
        due_time = datetime.strptime(consultation.due, DATE_FORMAT)
        user_time = datetime.now(tz=user_timezone)

        # Important. This job starts every hour at 0 minutes 0 seconds, so we need to check only hour
        if user_time.hour == settings.daily_consultations_reminder_time.hour:
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
                logger.debug(
                    "Add %s to job queue. Start in 1 second for user %s",
                    send_reminder_now.__name__,
                    consultation.telegram_id,
                )

    if overdue:
        await daily_overdue_consulations_reminder_job(context, overdue)