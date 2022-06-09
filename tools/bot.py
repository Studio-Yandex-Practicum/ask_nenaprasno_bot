import asyncio

from telegram import Bot
from telegram.ext import Application
from typing import Union

from logger import get_logger
from os_tools import get_secret

LOGGER = get_logger("Bot")
TOKEN = get_secret("TELEGRAM_TOKEN")
# --------------------------------------------------------------------------------------------- #
# Настройки webhook'а telegram bot'а                                                            #
# https://docs-python.ru/packages/biblioteka-python-telegram-bot-python/ispolzovanie-webhook/   #
# Следует создать и указать в config.py                                                         #
# --------------------------------------------------------------------------------------------- #
LISTEN_URL = "127.0.0.1"
LISTEN_PORT = 443
URL_PATH = TOKEN
CERTIFICATE = "cert.pem"
PRIVATE_KEY = "private.key"
WEBHOOK_URL = "https://some.url/" + TOKEN
# --------------------------------------------------------------------------------------------- #


async def send_message(chat_id: Union[str, int], text: str, message_type: str = "text"):
    """
    Отправка сообщения с использованием telegram bot (пользователь должен инициализировать чат
    с ботом, чтобы сообщение отправилось)
    :param chat_id: id чата пользователя для отправки сообщения.
    :param text: текст сообщения
    :param message_type: тип сообщения для отправки: text - для текстовых сообщений, ...
    """
    bot = Bot(TOKEN)
    if message_type.lower() == "text":
        await bot.send_message(text=text, chat_id=chat_id)
        LOGGER.debug("Сообщение успешно доставлено.")
    else:
        exc = "Тип сообщения временно не поддерживается."
        LOGGER.warning(exc)
        raise TypeError(exc)


async def init():
    app = Application.builder().token(TOKEN).build()
    if not app.bot.set_webhook(WEBHOOK_URL):
        exc = "Не удалось запустить webhook telegram bot'а"
        LOGGER.error(exc)
        raise AttributeError(exc)
    return app

