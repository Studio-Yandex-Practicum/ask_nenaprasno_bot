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

from constants import callback_data
from constants.jobs import (
    DAILY_CONSULTATIONS_REMINDER_JOB,
    DAILY_OVERDUE_CONSULTATIONS_REMINDER_JOB,
    USER_BILL_REMINDER_TEMPLATE,
)
from conversation.authorization import authorization_conversation
from core import config
from core.send_message import edit_message
from jobs import (
    daily_consulations_duedate_is_today_reminder_job,
    daily_consulations_reminder_job,
    monthly_bill_reminder_job,
    monthly_stat_job,
    weekly_stat_job,
)
from service.repeat_message import repeat_message_after_1_hour_callback
from texts import bot as texts_bot


async def skip_bill_callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Delete button under message."""
    await edit_message(update, update.callback_query.message.text_markdown_urled)
    await update.callback_query.answer()  # close progress bar in chat


async def done_bill_callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Delete job from JobQueue."""
    query = update.callback_query
    user_id = query.from_user.id
    job_name = USER_BILL_REMINDER_TEMPLATE.format(telegram_id=user_id)
    current_jobs = context.job_queue.get_jobs_by_name(job_name)
    for job in current_jobs:
        job.schedule_removal()
    await edit_message(update, texts_bot.REMIND_IN_NEXT_MONTH)
    await query.answer()  # close progress bar in chat


def create_bot():
    """
    Create telegram bot application
    :return: Created telegram bot application
    """
    bot_persistence = PicklePersistence(filepath=config.BOT_PERSISTENCE_FILE)
    bot_app = (
        ApplicationBuilder()
        .token(config.TOKEN)
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
        time=config.STAT_COLLECTION_TIME,
        days=config.WEEKLY_STAT_WEEK_DAYS,
    )
    # Once per month bot sends bill reminder (default: 1st day of month)
    bot_app.job_queue.run_monthly(
        monthly_bill_reminder_job,
        when=config.STAT_COLLECTION_TIME,
        day=config.MONTHLY_RECEIPT_REMINDER_DAY,
    )

    # Once per month bot sends previous month statistics
    bot_app.job_queue.run_monthly(
        monthly_stat_job,
        when=config.STAT_COLLECTION_TIME,
        day=config.MONTHLY_STAT_DAY,
    )

    # Once per day (but for every time zone) bot collects overdue consultations and send reminder
    # Doctor receives reminder at DAILY_OVERDUE_CONSULTATIONS_REMINDER_JOB his time zone
    bot_app.job_queue.run_repeating(
        daily_consulations_reminder_job,
        interval=timedelta(hours=1),
        first=time(hour=0, minute=0, second=0),
        name=DAILY_OVERDUE_CONSULTATIONS_REMINDER_JOB,
    )

    # Once per day at UTC+0 bot collects consultations where due_date is today and sends reminder to Doctor
    # at due_time + 1 hour
    bot_app.job_queue.run_daily(
        daily_consulations_duedate_is_today_reminder_job,
        time=config.DAILY_COLLECT_CONSULTATIONS_TIME,
        name=DAILY_CONSULTATIONS_REMINDER_JOB,
    )

    # Initial data collection for daily consultation on bot start up
    bot_app.job_queue.run_once(daily_consulations_reminder_job, when=timedelta(seconds=1))
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
        url=urljoin(config.APPLICATION_URL, "telegramWebhookApi"), secret_token=config.SECRET_TELEGRAM_TOKEN
    )
    return bot_app


def init_polling() -> None:
    """
    Init bot polling
    :return: Initiated application
    """
    bot_app = create_bot()
    bot_app.run_polling()
