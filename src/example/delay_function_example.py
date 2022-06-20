from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Application, CallbackQueryHandler, CommandHandler, ContextTypes

from src.constants.command_constants import COMMAND_HOUR_REMIND
from src.core.config import TOKEN
from src.service.delay import delay_message_for_1_hour_callback, delay_one_hour_button


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Sends a message with inline buttons attached."""
    keyboard = [
        [delay_one_hour_button],
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text("are you want to repeat after minute?", reply_markup=reply_markup)


def main() -> None:
    """Run the bot."""
    application = Application.builder().token(TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(delay_message_for_1_hour_callback, pattern=COMMAND_HOUR_REMIND))
    application.run_polling()


if __name__ == "__main__":
    main()
