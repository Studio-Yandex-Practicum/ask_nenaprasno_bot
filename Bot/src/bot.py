from telegram import Update
from telegram.ext import Application, ApplicationBuilder, CommandHandler, CallbackContext
from typing import Union

from core import config


async def start(update: Update, context: CallbackContext) -> None:
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Привет! Я постараюсь помочь вам.")


def init(webhook: bool = False) -> Application:
    """
    Init telegram bot application
    :param webhook: If True init webhook application else pooling
    :return: Initiated telegram bot application
    """
    app = (Application.builder() if webhook else ApplicationBuilder()).token(config.TOKEN).build()

    app.add_handler(CommandHandler("start", start))

    return app

