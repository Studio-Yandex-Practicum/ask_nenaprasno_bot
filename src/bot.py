from telegram import Update
from telegram.ext import (
    Application, ApplicationBuilder, CommandHandler, CallbackContext
)
from core import config


async def start(update: Update, context: CallbackContext) -> None:
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Привет! Я постараюсь помочь вам."
    )


async def weekly_stat_job(context: CallbackContext) -> None:
    """
    Send weekly statistics on the number of requests in the work
    """
    pass


async def monthly_receipt_reminder_job(context: CallbackContext) -> None:
    """
    Send monthly reminder about the receipt formation during payment
    Only for self-employed users
    """
    pass


async def monthly_stat_job(context: CallbackContext) -> None:
    """
    Send monthly statistics on the number of successfully
    closed requests.
    Only if the user had requests
    """
    pass


def create_bot():
    """
    Create telegram bot application
    :return: Created telegram bot application
    """
    bot_app = ApplicationBuilder().token(config.TOKEN).build()
    bot_app.add_handler(CommandHandler("start", start))
    bot_app.job_queue.run_daily(
        weekly_stat_job,
        time=config.WEEKLY_STAT_TIME,
        days=config.WEEKLY_STAT_WEEK_DAYS
    )
    bot_app.job_queue.run_monthly(
        monthly_receipt_reminder_job,
        when=config.MONTHLY_RECEIPT_REMINDER_TIME,
        day=config.MONTHLY_RECEIPT_REMINDER_DAY
    )
    bot_app.job_queue.run_monthly(
        monthly_stat_job,
        when=config.MONTHLY_STAT_TIME,
        day=config.MONTHLY_STAT_DAY
    )
    return bot_app


async def init_webhook() -> Application:
    """
    Init bot webhook
    :return: Initiated application
    """
    bot_app = create_bot()
    bot_app.updater = None
    await bot_app.bot.set_webhook(url=f"{config.WEBHOOK_URL}/telegram")
    return bot_app


def init_polling() -> None:
    """
    Init bot polling
    :return: Initiated application
    """
    bot_app = create_bot()
    bot_app.run_polling()
