from dataclasses import dataclass
from datetime import date, datetime, timedelta, timezone
from typing import Optional

from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext

from constants.callback_data import CALLBACK_DONE_BILL_COMMAND, CALLBACK_SKIP_BILL_COMMAND
from constants.timezone import MOSCOW_TIME_OFFSET
from conversation.menu import format_average_user_answer_time, format_rating
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
    "Время и стекло 😎\n" "Заявка - {consultation_number}\n" "Верим и ждем.\n\n"
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

service = APIService()


@dataclass(frozen=True)
class BaseConsultationData:
    """Stores structured data that is passed
    within a job to the job_queue of the bot.
    """

    consultation: Consultation
    message_template: Optional[str]

    async def get_due_date(self):
        """Returns due date or None."""
        consultation = await service.get_consultation(self.consultation.id)
        if (consultation is None) or (consultation.due is None):
            return None
        return datetime.strptime(consultation.due, DATE_FORMAT).date()


@dataclass(frozen=True)
class DueConsultationData(BaseConsultationData):
    """Stores structured data to be passed
    right upon expiration of the due time.
    """

    message_template: str = DUE_REMINDER_TEMPLATE

    async def is_valid(self):
        """Checks if consulation status is still valid."""
        return await self.get_due_date() == date.today()


@dataclass(frozen=True)
class DueHourConsultationData(BaseConsultationData):
    """Stores structured data to be passed
    one hour after expiration of the due time.
    """

    message_template: str = DUE_HOUR_REMINDER_TEMPLATE

    async def is_valid(self):
        """Checks if consulation status is still valid."""
        return await self.get_due_date() == date.today()


@dataclass(frozen=True)
class PastConsultationData(BaseConsultationData):
    """Stores structured data to be passed
    for consultations expired at least one day ago.
    """

    message_template: str = PAST_REMINDER_TEMPLATE

    async def is_valid(self):
        """Checks if consulation status is still valid."""
        return await self.get_due_date() < date.today()


@dataclass(frozen=True)
class ForwardConsultationData(BaseConsultationData):
    """Stores structured data to be passed
    for consultations expiring tomorrow.
    """

    message_template: str = FORWARD_REMINDER_TEMPLATE

    async def is_valid(self):
        """Checks if consulation status is still valid."""
        return await self.get_due_date() - date.today() == timedelta(days=1)


async def weekly_stat_job(context: CallbackContext) -> None:
    """Collects users timezones and adds statistic-sending jobs to queue."""
    week_statistics = await service.get_week_stat()
    # микропроблема: если у пользователя не выбрана таймзона, то в сете будет None,
    # который в send_weekly_statistic_job будет интрепретирован как таймзона по-умолчанию (МСК)
    # Получаетcя на МСК будет 2 джобы
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
            trello_id=config.TRELLO_BORD_ID,
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


async def send_reminder(context: CallbackContext) -> None:
    """Sends reminder to the user according to the message template.
    Prior to that, check if the consultation is still relevant.
    """
    job_data = context.job.data
    consultation = job_data.consultation
    message_template = job_data.message_template
    if await job_data.is_valid():
        telegram_id = consultation.telegram_id
        active_cons = await service.get_user_active_consultations(telegram_id)
        expired_cons = await service.get_user_expired_consultations(telegram_id)

        message = message_template.format(
            consultation_id=consultation.id,
            consultation_number=consultation.number,
            active_consultations=active_cons.active_consultations,
            expired_consultations=expired_cons.expired_consultations,
            site_url=build_consultation_url(consultation.id),
            trello_overdue_url=build_trello_url(consultation.username_trello, True),
            declination_consultation=get_word_case(active_cons.active_consultations, "заявка", "заявки", "заявок"),
            genitive_declination_consultation=get_word_genitive(expired_cons.expired_consultations, "заявки", "заявок"),
        )
        await send_message(bot=context.bot, chat_id=telegram_id, text=message)


async def daily_consulations_reminder_job(context: CallbackContext) -> None:
    """Adds a reminder job to the bot's job queue according
    to one of the following scenarios:
    - the due date is tomorrow;
    - the due date has just expired;
    - the due date expired one hour ago;
    - the due date expired at least one day ago.
    """
    now = datetime.utcnow()
    default_timezone = timezone(timedelta(hours=MOSCOW_TIME_OFFSET))
    consultations = await service.get_daily_consultations()
    for consultation in consultations:
        user_timezone = context.bot_data.get(int(consultation.telegram_id), default_timezone)
        due_time = datetime.strptime(consultation.due, DATE_FORMAT)
        if due_time.date() == now.date():
            context.job_queue.run_once(send_reminder, when=due_time, data=DueConsultationData(consultation))
            context.job_queue.run_once(
                send_reminder, when=due_time + timedelta(hours=1), data=DueHourConsultationData(consultation)
            )
        elif due_time.date() < date.today():
            context.job_queue.run_once(
                send_reminder,
                when=config.DAILY_CONSULTATIONS_REMINDER_TIME.replace(tzinfo=user_timezone),
                data=PastConsultationData(consultation),
            )
        elif (due_time.date() - now.date()) == timedelta(days=1):
            context.job_queue.run_once(
                send_reminder,
                when=config.DAILY_CONSULTATIONS_REMINDER_TIME.replace(tzinfo=user_timezone),
                data=ForwardConsultationData(consultation),
            )
