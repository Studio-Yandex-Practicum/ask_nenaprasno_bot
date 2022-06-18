from telegram import Update
from telegram.ext import (Application,
                          ApplicationBuilder,
                          CommandHandler,
                          CallbackContext)

from decorators.logger import async_error_logger, sync_error_logger
from core import config
from src.core.logger import bot_logger

logger = bot_logger


@async_error_logger(name='start', logger=logger)
async def start(update: Update, context: CallbackContext) -> None:
    await context.bot.send_message(chat_id=update.effective_chat.id,
                                   text="Привет! Я постараюсь помочь вам.")


@async_error_logger(name='test', logger=logger)
async def test(context: CallbackContext) -> None:
    """
    Send test message after running
    :param context: CallbackContext
    """
    chat_id = config.CHAT_ID
    await context.bot.send_message(chat_id=chat_id, text="Bot still running.")


@sync_error_logger(name='create_bot', logger=logger)
def create_bot():
    """
    Create telegram bot application
    :return: Created telegram bot application
    """
    bot_app = ApplicationBuilder().token(config.TOKEN).build()
    bot_app.add_handler(CommandHandler("start", start))
    bot_app.job_queue.run_repeating(test, config.TEST_PERIOD)
    return bot_app


@async_error_logger(name='init_webhook', logger=logger)
async def init_webhook() -> Application:
    """
    Init bot webhook
    :return: Initiated application
    """
    bot_app = create_bot()
    bot_app.updater = None
    await bot_app.bot.set_webhook(url=f"{config.WEBHOOK_URL}/telegram")
    return bot_app


@sync_error_logger(name='init_polling', logger=logger)
def init_polling() -> None:
    """
    Init bot polling
    :return: Initiated application
    """
    bot_app = create_bot()
    bot_app.run_polling()
