from telegram import Update
from telegram.ext import Application, ApplicationBuilder, CommandHandler, CallbackContext

import config


async def start(update: Update, context: CallbackContext.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Привет! Я постараюсь помочь вам.")


async def init_webhook() -> Application:
    """
    Init bot webhook
    :return: initiated application
    """
    app = Application.builder().updater(None).token(config.TOKEN).build()

    app.add_handler(CommandHandler("start", start))

    await app.bot.set_webhook(url=f"{config.WEBHOOK_URL}/telegram")
    return app


def init_pooling() -> Application:
    """
    Init bot pooling
    :return: initiated application
    """
    app = ApplicationBuilder().token(config.TOKEN).build()

    app.add_handler(CommandHandler("start", start))

    app.run_polling()
    return app
