import asyncio
import html
import uvicorn

from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import PlainTextResponse, Response
from starlette.routing import Route
from telegram import Update
from telegram.ext import Application, ApplicationBuilder, CommandHandler, CallbackContext, ContextTypes, ExtBot

from logger import get_logger
from os_tools import get_secret

logger = get_logger("Bot")
# --------------------------------------------------------------------------------------------- #
# Следует создать и указать в config.py настройки webhook'а telegram bot'а                      #
# https://github.com/python-telegram-bot/python-telegram-bot/wiki/Webhooks                      #
# --------------------------------------------------------------------------------------------- #
TOKEN = get_secret("TELEGRAM_TOKEN")
HOST = "127.0.0.1"
PORT = int(get_secret("BOT_PORT"))
WEBHOOK_URL = get_secret("WEBHOOK_URL")
CHAT_ID = get_secret("CHAT_ID")
# --------------------------------------------------------------------------------------------- #

async def start(update: Update, context: CallbackContext.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Привет! Я постараюсь помочь вам.")


async def init_webhook() -> None:
    app = Application.builder().updater(None).token(TOKEN).build()
    app.bot_data["url"] = WEBHOOK_URL
    app.bot_data["admin_chat_id"] = CHAT_ID

    app.add_handler(CommandHandler("start", start))
    # -------------------------------------------- #
    # Здесь добавляются хэндлеры                   #
    # -------------------------------------------- #
    await app.bot.set_webhook(url=f"{WEBHOOK_URL}/telegram")

    async def telegram(request: Request) -> Response:
        await app.update_queue.put(
            Update.de_json(data=await request.json(), bot=app.bot)
        )
        return Response()

    async def health(_: Request) -> PlainTextResponse:
        return PlainTextResponse(content="The bot is still running fine :)")

    starlette_app = Starlette(
        routes=[
            Route("/telegram", telegram, methods=["POST"]),
            Route("/health", health, methods=["GET"]),
        ]
    )
    webserver = uvicorn.Server(
        config=uvicorn.Config(
            app=starlette_app,
            port=PORT,
            use_colors=False,
            host=HOST,
        )
    )
    async with app:
        await app.start()
        await webserver.serve()
        await app.stop()


def init_pooling():
    app = ApplicationBuilder().token(TOKEN).build()
    start_handler = CommandHandler('start', start)
    # -------------------------------------------- #
    # Здесь добавляются хэндлеры                   #
    # -------------------------------------------- #
    app.add_handler(start_handler)
    app.run_polling()
    return app


asyncio.run(init_webhook())
init_pooling()