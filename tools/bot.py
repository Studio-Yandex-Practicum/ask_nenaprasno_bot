import asyncio
from telegram import Bot
from telegram.ext import Application
from typing import Union

from logger import get_logger
from os_tools import get_secret

LOGGER = get_logger("Bot")
# --------------------------------------------------------------------------------------------- #
# Настройки webhook'а telegram bot'а                                                            #
# https://github.com/python-telegram-bot/python-telegram-bot/wiki/Webhooks                      #
# Следует создать и указать в config.py                                                         #
# --------------------------------------------------------------------------------------------- #
TOKEN = get_secret("TELEGRAM_TOKEN")
LISTEN_URL = "127.0.0.1"
LISTEN_PORT = 443
URL_PATH = TOKEN
CERTIFICATE = "cert.pem"
PRIVATE_KEY = "private.key"
WEBHOOK_URL = "https://some.url/" + TOKEN
# --------------------------------------------------------------------------------------------- #


async def init() -> Application:
    """
    Make telegram bot base including dispatcher, bot, updater, etc.
    :return:
    """
    app = Application.builder().token(TOKEN).build()
    if not await app.bot.set_webhook(WEBHOOK_URL):
        exc = "Не удалось запустить webhook telegram bot'а"
        LOGGER.error(exc)
        raise AttributeError(exc)
    return app

asyncio.run(init())
