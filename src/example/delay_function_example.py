from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (Application, CallbackQueryHandler, CommandHandler,
                          ContextTypes)

from src.core.config import TOKEN
from src.service.delay import delay_message_for_1_hour


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Sends a message with inline buttons attached."""
    keyboard = [
        [InlineKeyboardButton("repeat after minute", callback_data="repeat")],
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        "are you want to repeat after minute?",
        reply_markup=reply_markup
    )


def main() -> None:
    """Run the bot."""
    application = Application.builder().token(TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(
        CallbackQueryHandler(delay_message_for_1_hour, pattern="delay")
    )
    application.run_polling()


if __name__ == "__main__":
    main()
