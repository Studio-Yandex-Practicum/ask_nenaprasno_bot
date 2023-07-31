from telegram.ext import CallbackContext

from bot.constants.jobs import USER_BILL_REMINDER_TEMPLATE
from bot.conversation import menu as mn
from bot.decorators.logger import async_job_logger
from bot.jobs import daily, templates
from bot.services.timezone_service import get_timezone_from_str, get_user_timezone
from core.config import settings
from core.logger import logger
from core.send_message import send_message
from core.utils import build_trello_url
from service.api_client import APIService

__api = APIService()


@async_job_logger
async def monthly_stat_job(context: CallbackContext) -> None:
    """Collects users timezones and adds statistic-sending jobs to queue."""
    logger.debug("Running monthly_stat_job")
    month_statistics = await __api.get_month_stat()

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
async def send_monthly_statistic_job(context: CallbackContext) -> None:
    """Send monthly statistic to user."""
    logger.debug("Running send_monthly_statistic_job")
    statistic = context.job.data
    message = templates.MONTHLY_STATISTIC_TEMPLATE.format(
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
    bill_stat = await __api.get_bill()
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
            daily.daily_bill_remind_job,
            time=start_time,
            name=job_name,
            chat_id=telegram_id,
        )
        logger.debug(
            "Add %s to job queue. Start at %s for user %s",
            daily.daily_bill_remind_job.__name__,
            start_time,
            telegram_id,
        )
