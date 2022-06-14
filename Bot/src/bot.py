from contextlib import asynccontextmanager
from starlette.applications import Starlette
from telegram import Update
from telegram.ext import Application, ApplicationBuilder, CommandHandler, CallbackContext
from typing import AsyncGenerator

from core import config


async def start(update: Update, context: CallbackContext) -> None:
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Привет! Я постараюсь помочь вам.")


async def test(context: CallbackContext) -> None:
    """
    Send test message after running
    :param context: CallbackContext
    """
    bot_id = 971967681
    await context.bot.send_message(chat_id=bot_id, text="HGHJKLKJHLKJH")


def create_bot():
    """
    Create telegram bot application
    :return: Created telegram bot application
    """
    bot_app = ApplicationBuilder().token(config.TOKEN).build()
    bot_app.add_handler(CommandHandler("start", start))
    bot_app.job_queue.run_repeating(test, 10)
    return bot_app


async def init_webhook() -> Application:
    """
    Init bot webhook
    :return: Initiated application
    """
    bot_app = create_bot()
    bot_app.updater = None
    await bot_app.bot.set_webhook(url=f"{config.WEBHOOK_IP}/telegram")
    return bot_app


async def init_polling() -> None:
    """
    Init bot pooling
    :return: Initiated application
    """
    bot_app = create_bot()
    bot_app.run_polling()
