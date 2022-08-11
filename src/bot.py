from datetime import time

from telegram import Update
from telegram.ext import Application, ApplicationBuilder, CallbackQueryHandler, ContextTypes, PicklePersistence

from constants import callback_data
from constants.jobs import NAME_OVERDUE_REMINDER_JOB
from conversation import start_conversation
from core import config
from core.send_message import edit_message
from jobs import monthly_bill_reminder_job, monthly_stat_job, overdue_consult_reminder_job, weekly_stat_job
from service.repeat_message import repeat_message_after_1_hour_callback


async def skip_bill_callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Delete button under message"""
    await edit_message(update=update, new_text=update.callback_query.message.text_markdown_v2_urled)
    await update.callback_query.answer()  # close progress bar in chat


async def done_bill_callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Delete job from JobQueue
    """
    query = update.callback_query
    user_id = query.from_user.id
    current_jobs = context.job_queue.get_jobs_by_name(f"send_{user_id}_bill_until_complete")
    for job in current_jobs:
        job.schedule_removal()
    await edit_message(update=update, new_text="Не будем напоминать до следующего месяца")
    await query.answer()  # close progress bar in chat


def create_bot():
    """
    Create telegram bot application
    :return: Created telegram bot application
    """
    bot_persistence = PicklePersistence(filepath=config.BOT_PERSISTENCE_FILE)
    bot_app = ApplicationBuilder().token(config.TOKEN).persistence(persistence=bot_persistence).build()
    bot_app.add_handler(start_conversation)
    bot_app.add_handlers(
        handlers=[
            CallbackQueryHandler(repeat_message_after_1_hour_callback, pattern=callback_data.CALLBACK_REPEAT_COMMAND),
            CallbackQueryHandler(done_bill_callback_handler, pattern=callback_data.CALLBACK_DONE_BILL_COMMAND),
            CallbackQueryHandler(skip_bill_callback_handler, pattern=callback_data.CALLBACK_SKIP_BILL_COMMAND),
        ]
    )
    bot_app.job_queue.run_daily(weekly_stat_job, time=config.WEEKLY_STAT_TIME, days=config.WEEKLY_STAT_WEEK_DAYS)
    bot_app.job_queue.run_monthly(
        monthly_bill_reminder_job, when=config.MONTHLY_RECEIPT_REMINDER_TIME, day=config.MONTHLY_RECEIPT_REMINDER_DAY
    )
    bot_app.job_queue.run_monthly(monthly_stat_job, when=config.MONTHLY_STAT_TIME, day=config.MONTHLY_STAT_DAY)
    bot_app.job_queue.run_daily(overdue_consult_reminder_job, time=time(0, 0), name=NAME_OVERDUE_REMINDER_JOB)
    return bot_app


async def init_webhook() -> Application:
    """
    Init bot webhook
    :return: Initiated application
    """
    bot_app = create_bot()
    bot_app.updater = None
    await bot_app.bot.set_webhook(
        url=f"{config.WEBHOOK_URL}/telegramWebhookApi", secret_token=config.SECRET_TELEGRAM_TOKEN
    )
    return bot_app


def init_polling() -> None:
    """
    Init bot polling
    :return: Initiated application
    """
    bot_app = create_bot()
    bot_app.run_polling()
