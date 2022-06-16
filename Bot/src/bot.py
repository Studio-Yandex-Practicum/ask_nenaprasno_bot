import asyncio

from telegram import Update
from telegram.ext import (ExtBot, ApplicationBuilder, CallbackContext,
                          CommandHandler)

from constants import commands, texts
from core import config
from site_handler import site_requests as from_site


async def send_message(
    context: CallbackContext, chat_id: int, text: str
) -> None:
    """
    Send message with handling errors.
    :param update: Update
    :param context: CallbackContext
    """
    try:
        await context.bot.send_message(
            chat_id=chat_id,
            text=text
        )
    except Exception:
        ...


async def help(update: Update, context: CallbackContext) -> None:
    """
    Send help message.
    :param update: Update
    :param context: CallbackContext
    """
    chat_id = update.effective_chat.id
    await send_message(context, chat_id, texts.HELP)


async def start(update: Update, context: CallbackContext) -> None:
    """Send greeting.
    :param update: Update
    :param context: CallbackContext
    """
    chat_id = update.effective_chat.id
    await send_message(context, chat_id, texts.GREETING)
    await asyncio.sleep(1)
    await send_message(context, chat_id, texts.ARE_YOUR_AN_EXPERT)


async def orders(update: Update, context: CallbackContext) -> None:
    """Send current orders.
    :param update: Update
    :param context: CallbackContext
    """
    chat_id = update.effective_chat.id
    user_id = update.effective_user.id
    current_orders = await from_site.get_current_orders(user_id)
    text = texts.CURRENT_ORDERS % (len(current_orders), current_orders)

    await send_message(context, chat_id, text)


async def overdue(update: Update, context: CallbackContext) -> None:
    """Send overdue orders.
    :param update: Update
    :param context: CallbackContext
    """
    chat_id = update.effective_chat.id
    user_id = update.effective_user.id
    overdue_orders = await from_site.get_overdue_orders(user_id)
    text = texts.OVERDUE_ORDERS % (len(overdue_orders), overdue_orders)
    await send_message(context, chat_id, text)


async def terms(update: Update, context: CallbackContext) -> None:
    """Send terms.
    :param update: Update
    :param context: CallbackContext
    """
    chat_id = update.effective_chat.id
    await send_message(context, chat_id, texts.TERMS)


async def test(context: CallbackContext) -> None:
    """
    Send test message after running
    :param context: CallbackContext
    """
    chat_id = config.CHAT_ID
    await send_message(context, chat_id, "Bot still running.")


def create_bot() -> ExtBot:
    """
    Create telegram bot application
    :return: Created telegram bot application
    """
    bot_app: ExtBot = ApplicationBuilder().token(config.TOKEN).build()
    bot_app.add_handlers([
        CommandHandler(commands.HELP, help),
        CommandHandler(commands.START, start),
        CommandHandler(commands.ORDERS, orders),
        CommandHandler(commands.OVERDUE, overdue),
        CommandHandler(commands.TERMS, terms)
    ])
    bot_app.job_queue.run_repeating(test, config.TEST_PERIOD)
    return bot_app


async def init_webhook() -> ExtBot:
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
