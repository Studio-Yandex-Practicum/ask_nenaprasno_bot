from telegram import Update
from telegram.ext import Application, ApplicationBuilder, CommandHandler, CallbackContext

import config


async def start(update: Update, context: CallbackContext.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Привет! Я постараюсь помочь вам.")


def add_handlers(app: Application) -> None:
    """
    Add handlers to telegram bot application
    :param app: Telegram bot application
    """
    handlers = {
        CommandHandler: (
            ("start", start),
        ),
    }
    for handler in handlers:
        for params in handlers[handler]:
            app.add_handler(handler(*params))


async def init_webhook() -> Application:
    """
    Init webhook bot
    """
    app = Application.builder().updater(None).token(config.TOKEN).build()

    add_handlers(app)

    await app.bot.set_webhook(url=f"{config.WEBHOOK_URL}/telegram")
    return app


def init_pooling():
    app = ApplicationBuilder().token(config.TOKEN).build()

    add_handlers(app)

    app.run_polling()
    return app
