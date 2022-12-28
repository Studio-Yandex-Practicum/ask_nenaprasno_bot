from datetime import time, timedelta
from urllib.parse import urljoin

from telegram import Update
from telegram.ext import (
    AIORateLimiter,
    Application,
    ApplicationBuilder,
    CallbackQueryHandler,
    ContextTypes,
    PicklePersistence,
)

from bot.constants import callback_data, jobs
from bot.conversation.authorization import authorization_conversation
from bot.decorators.logger import async_error_logger
from bot.jobs import (
    daily_consulations_duedate_is_today_reminder_job,
    daily_consulations_reminder_job,
    monthly_bill_reminder_job,
    monthly_stat_job,
    weekly_stat_job,
)
from bot.service.repeat_message import repeat_message_after_1_hour_callback
from core.config import settings
from core.logger import logger
from core.send_message import edit_message


@async_error_logger(name="skip_bill_callback_handler")
async def skip_bill_callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Delete button under message."""
    await edit_message(update, update.callback_query.message.text_markdown_urled)
    await update.callback_query.answer()  # close progress bar in chat


@async_error_logger(name="done_bill_callback_handler")
async def done_bill_callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Delete job from JobQueue."""
    query = update.callback_query
    user_id = query.from_user.id
    job_name = jobs.USER_BILL_REMINDER_TEMPLATE.format(telegram_id=user_id)
    current_jobs = context.job_queue.get_jobs_by_name(job_name)
    for job in current_jobs:
        job.schedule_removal()
        logger.debug("Remove %s from queue", job.name)
    await edit_message(update, "Не будем напоминать до следующего месяца")
    await query.answer()  # close progress bar in chat


def create_bot():
    """
    Create telegram bot application
    :return: Created telegram bot application
    """
    bot_persistence = PicklePersistence(filepath=settings.bot_persistence_file)
    bot_app = (
        ApplicationBuilder()
        .token(settings.telegram_token)
        .rate_limiter(AIORateLimiter())
        .persistence(persistence=bot_persistence)
        .build()
    )
    # Handler: first words of bot to new user
    bot_app.add_handler(authorization_conversation)
    # Handlers: bills
    bot_app.add_handlers(
        handlers=[
            # When user asks to remind about bill after 1 hour
            CallbackQueryHandler(repeat_message_after_1_hour_callback, pattern=callback_data.CALLBACK_REPEAT_COMMAND),
            # When user hit button "Уже отправил(а)"
            CallbackQueryHandler(done_bill_callback_handler, pattern=callback_data.CALLBACK_DONE_BILL_COMMAND),
            # When user hit button "Скоро отправлю"
            CallbackQueryHandler(skip_bill_callback_handler, pattern=callback_data.CALLBACK_SKIP_BILL_COMMAND),
        ]
    )
    # Once per week bot sends current week statistics (default: friday)
    bot_app.job_queue.run_daily(
        weekly_stat_job,
        time=settings.stat_collection_time,
        days=(settings.weekly_stat_week_days,),
    )
    # Once per month bot sends bill reminder (default: 1st day of month)
    bot_app.job_queue.run_monthly(
        monthly_bill_reminder_job,
        when=settings.stat_collection_time,
        day=settings.monthly_receipt_reminder_day,
    )

    # Once per month bot sends previous month statistics
    bot_app.job_queue.run_monthly(
        monthly_stat_job,
        when=settings.stat_collection_time,
        day=settings.monthly_stat_day,
    )

    # Once per day (but for every time zone) bot collects overdue consultations and send reminder
    # Doctor receives reminder at DAILY_OVERDUE_CONSULTATIONS_REMINDER_JOB his time zone
    bot_app.job_queue.run_repeating(
        daily_consulations_reminder_job,
        interval=timedelta(hours=1),
        first=time(minute=int(settings.daily_consultations_reminder_time.minute)),
        name=jobs.DAILY_OVERDUE_CONSULTATIONS_REMINDER_JOB,
    )

    # Once per day at UTC+0 bot collects consultations where due_date is today and sends reminder to Doctor
    # at due_time + 1 hour
    bot_app.job_queue.run_daily(
        daily_consulations_duedate_is_today_reminder_job,
        time=settings.daily_collect_consultation_time,
        name=jobs.DAILY_CONSULTATIONS_REMINDER_JOB,
    )

    # Initial data collection for daily consultation on bot start up
    bot_app.job_queue.run_once(daily_consulations_duedate_is_today_reminder_job, when=timedelta(seconds=1))

    return bot_app


async def init_webhook() -> Application:
    """
    Init bot webhook
    :return: Initiated application
    """
    bot_app = create_bot()
    bot_app.updater = None
    await bot_app.bot.set_webhook(
        url=urljoin(settings.application_url, "telegramWebhookApi"), secret_token=settings.secret_telegram_token
    )
    logger.debug("Set webhook. App url: %s", settings.application_url)
    return bot_app


def init_polling() -> None:
    """
    Init bot polling
    :return: Initiated application
    """
    bot_app = create_bot()
    bot_app.run_polling()
    logger.debug("Start polling")


def init_polling_api() -> Application:
    """
    Init bot polling with API
    :return: Initiated application
    """
    bot_app = create_bot()
    logger.debug("Start polling with API")
    return bot_app
