from contextlib import asynccontextmanager
from starlette.applications import Starlette
from telegram import Update
from telegram.ext import Application, ApplicationBuilder, CommandHandler, CallbackContext
from typing import AsyncGenerator

from core import config


async def start(update: Update, context: CallbackContext) -> None:
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Привет! Я постараюсь помочь вам.")


def create_bot():
    """
    Create telegram bot application
    :return: Created telegram bot application
    """
    app = ApplicationBuilder().token(config.TOKEN).build()

    app.add_handler(CommandHandler("start", start))

    return app


@asynccontextmanager
async def init() -> AsyncGenerator[Application, None]:
    """
    Init bot webhook
    :return: Webhook application generator
    """
    bot_app = create_bot()
    bot_app.updater = None
    await bot_app.bot.set_webhook(url=f"{config.WEBHOOK_IP}/telegram")
    async with bot_app:
        await bot_app.start()
        try:
            yield bot_app
        finally:
            await bot_app.stop()


@asynccontextmanager
async def manage_bot(api: Starlette) -> AsyncGenerator:
    """
    Create bot managing generator
    :param api: Starlette application api
    :return: Async generator
    """
    async with init() as bot:
        # ------------------------------------------------- #
        # Adding bot application into Starlette api context #
        # for using it later like send messages or replies  #
        # ------------------------------------------------- #
        api.state.bot = bot
        yield


if __name__ == '__main__':
    create_bot().run_polling()
