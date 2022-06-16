from contextlib import asynccontextmanager
from starlette.applications import Starlette
from telegram import Update
from telegram.ext import (
    Application, ApplicationBuilder, CommandHandler, CallbackContext
)
from typing import AsyncGenerator

from core import config


async def start(update: Update, context: CallbackContext) -> None:
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Привет! Я постараюсь помочь вам."
    )
    context.job_queue.run_daily(
        week_stat,
        time=config.TIME,
        days=config.WEEK_DAYS
    )
    context.job_queue.run_monthly(
        receipt_reminder,
        when=config.TIME,
        day=config.DAY
    )
    context.job_queue.run_monthly(
        month_stat,
        when=config.TIME,
        day=config.DAY
    )


async def test(context: CallbackContext) -> None:
    """
    Send test message after running
    :param context: CallbackContext
    """
    chat_id = config.CHAT_ID
    await context.bot.send_message(chat_id=chat_id, text="Bot still running.")


async def week_stat(context: CallbackContext) -> None:
    """
    Send weekly statistics on the number of requests in the work
    """
    await context.bot.send_message(
        chat_id=config.CHAT_ID,
        text="За прошедшую неделю у вас было заявок..."
    )


async def receipt_reminder(context: CallbackContext) -> None:
    """
    Send monthly reminder about the receipt formation during payment
    Only for self-employed users
    """
    await context.bot.send_message(
        chat_id=config.CHAT_ID,
        text="Пожалуйста, пришлите чек на @mail.ru"
    )


async def month_stat(context: CallbackContext) -> None:
    """
    Send monthly statistics on the number of successfully
    closed requests.
    Only if the user had requests
    """
    await context.bot.send_message(
        chat_id=config.CHAT_ID,
        text="В прошедшем месяце вы ответили на ... заявок"
    )


def create_bot():
    """
    Create telegram bot application
    :return: Created telegram bot application
    """
    bot_app = ApplicationBuilder().token(config.TOKEN).build()
    bot_app.add_handler(CommandHandler("start", start))
    bot_app.job_queue.run_repeating(test, config.TEST_PERIOD)
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


async def init_polling() -> None:
    """
    Init bot pooling
    :return: Initiated application
    """
    bot_app = create_bot()
    bot_app.run_polling()
