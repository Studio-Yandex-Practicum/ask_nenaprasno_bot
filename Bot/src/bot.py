from telegram import Update
from telegram.ext import Application, ApplicationBuilder, CommandHandler, CallbackContext
from contextlib import asynccontextmanager
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
    bot = create_bot()
    bot.updater = None
    # ------------------------------------------------------------- #
    # Can be used config.WEBHOOK_URL or config.WEBHOOK_IP           #
    # ------------------------------------------------------------- #
    await bot.bot.set_webhook(url=f"{config.WEBHOOK_URL}/telegram")
    async with bot:
        await bot.start()
        try:
            yield bot
        finally:
            await bot.stop()


if __name__ == '__main__':
    create_bot().run_polling()
