import asyncio
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from starlette.applications import Starlette
from telegram import Update
from telegram.ext import (Application, ApplicationBuilder, CallbackContext,
                          CommandHandler, MessageHandler)

from constants import commands, texts
from core import config
from site_handler import site_requests as from_site


async def help(update: Update, context: CallbackContext) -> None:
    """
    Send help message.
    :param update: Update
    :param context: CallbackContext
    """
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=texts.HELP
    )


async def start(update: Update, context: CallbackContext) -> None:
    """Send greeting.
    :param update: Update
    :param context: CallbackContext
    """
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=texts.GREETING
    )
    await asyncio.sleep(1)
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=texts.ARE_YOUR_AN_EXPERT
    )


async def orders(update: Update, context: CallbackContext) -> None:
    """Send current orders.
    :param update: Update
    :param context: CallbackContext
    """
    user_id = update.effective_user.id
    current_orders = await from_site.get_current_orders(user_id)
    text = texts.CURRENT_ORDERS % (len(current_orders), current_orders)

    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=text
    )


async def overdue(update: Update, context: CallbackContext) -> None:
    """Send overdue orders.
    :param update: Update
    :param context: CallbackContext
    """
    user_id = update.effective_user.id
    overdue_orders = await from_site.get_overdue_orders(user_id)
    text = texts.OVERDUE_ORDERS % (len(overdue_orders), overdue_orders)

    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=text
    )


async def terms(update: Update, context: CallbackContext) -> None:
    """Send terms.
    :param update: Update
    :param context: CallbackContext
    """
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=texts.TERMS
    )


async def test(context: CallbackContext) -> None:
    """
    Send test message after running
    :param context: CallbackContext
    """
    chat_id = config.CHAT_ID
    await context.bot.send_message(chat_id=chat_id, text="Bot still running.")


def create_bot() -> Application:
    """
    Create telegram bot application
    :return: Created telegram bot application
    """
    bot_app: Application = ApplicationBuilder().token(config.TOKEN).build()
    bot_app.add_handler(CommandHandler(commands.HELP, help))
    bot_app.add_handler(CommandHandler(commands.START, start))
    bot_app.add_handler(CommandHandler(commands.ORDERS, orders))
    bot_app.add_handler(CommandHandler(commands.OVERDUE, overdue))
    bot_app.add_handler(CommandHandler(commands.TERMS, terms))
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


def init_polling() -> None:
    """
    Init bot pooling
    :return: Initiated application
    """
    bot_app = create_bot()
    bot_app.run_polling()
