from telegram import InlineKeyboardMarkup, Update
from telegram.ext import Application, CallbackQueryHandler, CommandHandler, ContextTypes

from src.constants.callback_data import CALLBACK_REPEAT_COMMAND
from src.core.config import TOKEN
from src.service.repeat_message import repeat_after_one_hour_button, repeat_message_after_1_hour_callback


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Sends a message with inline buttons attached."""
    keyboard = [
        [repeat_after_one_hour_button],
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text("are you want to repeat after minute?", reply_markup=reply_markup)


def main() -> None:
    """Run the bot."""
    application = Application.builder().token(TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(repeat_message_after_1_hour_callback, pattern=CALLBACK_REPEAT_COMMAND))
    application.run_polling()


if __name__ == "__main__":
    main()
