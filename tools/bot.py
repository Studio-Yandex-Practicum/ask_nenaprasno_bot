import asyncio


from telegram import Bot, error, Update
from telegram.ext import JobQueue
from queue import Queue
from threading import Thread
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

# --------------------------------------------------------------------------------------------- #
# Инициализация бота                                                                            #
# --------------------------------------------------------------------------------------------- #
async def check_bot(bot):
    try:
        await bot.get_me()
    except Exception as exception:
        LOGGER.error(exception)
        raise exception
    else:
        LOGGER.debug("Bot has been loaded.")


if not (BOT := None):
    BOT = Bot(TOKEN)
    asyncio.run(check_bot(BOT))
# ---------------------------------------------------------------------------------------------- #


async def send_message(chat_id: Union[str, int], text: str, message_type: str = "text"):
    """
    Отправка сообщения с использованием telegram bot (пользователь должен инициализировать чат
    с ботом, чтобы сообщение отправилось)
    :param chat_id: id чата пользователя для отправки сообщения.
    :param text: текст сообщения
    :param message_type: тип сообщения для отправки: text - для текстовых сообщений, ...
    """
    if message_type.lower() == "text":
        await BOT.send_message(text=text, chat_id=chat_id)
        LOGGER.info("Сообщение успешно доставлено.")
    else:
        exc = "Тип сообщения временно не поддерживается."
        LOGGER.warning(exc)
        raise TypeError(exc)


async def bot_init():
    await BOT.set_webhook()
