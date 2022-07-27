from telegram.ext import Application, ApplicationBuilder, PicklePersistence

from conversation import start_conversation
from core import config
from jobs import monthly_bill_reminder_job, monthly_stat_job, weekly_stat_job


def create_bot():
    """
    Create telegram bot application
    :return: Created telegram bot application
    """
    bot_persistence = PicklePersistence(filepath=config.BOT_PERSISTENCE_FILE)
    bot_app = ApplicationBuilder().token(config.TOKEN).persistence(persistence=bot_persistence).build()
    bot_app.add_handler(start_conversation)
    bot_app.job_queue.run_daily(weekly_stat_job, time=config.WEEKLY_STAT_TIME, days=config.WEEKLY_STAT_WEEK_DAYS)
    bot_app.job_queue.run_monthly(
        monthly_bill_reminder_job, when=config.MONTHLY_RECEIPT_REMINDER_TIME, day=config.MONTHLY_RECEIPT_REMINDER_DAY
    )
    bot_app.job_queue.run_monthly(monthly_stat_job, when=config.MONTHLY_STAT_TIME, day=config.MONTHLY_STAT_DAY)
    return bot_app


async def init_webhook() -> Application:
    """
    Init bot webhook
    :return: Initiated application
    """
    bot_app = create_bot()
    bot_app.updater = None
    await bot_app.bot.set_webhook(url=f"{config.WEBHOOK_URL}")
    return bot_app


def init_polling() -> None:
    """
    Init bot polling
    :return: Initiated application
    """
    bot_app = create_bot()
    bot_app.run_polling()
