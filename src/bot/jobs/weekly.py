from telegram.ext import CallbackContext

from bot.decorators.logger import async_job_logger
from bot.jobs import templates
from bot.services.timezone_service import get_timezone_from_str
from core.config import settings
from core.logger import logger
from core.send_message import send_message
from core.utils import build_trello_url, get_word_case, get_word_genitive
from service.api_client import APIService

__api = APIService()


@async_job_logger
async def weekly_stat_job(context: CallbackContext) -> None:
    """Collects users timezones and adds statistic-sending jobs to queue."""
    logger.debug("Running weekly_stat_job")
    week_statistics = await __api.get_week_stat()
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
async def send_weekly_statistic_job(context: CallbackContext) -> None:
    """Sends weekly statistics to users with specific timezone."""
    logger.debug("Running send_weekly_statistic_job")
    current_tz = context.job.data
    week_statistics = await __api.get_week_stat()

    for statistic in filter(lambda stat: stat.telegram_id is not None and stat.timezone == current_tz, week_statistics):
        message = templates.WEEKLY_STATISTIC_TEMPLATE.format(
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
