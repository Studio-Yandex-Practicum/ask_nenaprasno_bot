from datetime import timedelta

from telegram import Update
from telegram.ext import Application, CallbackQueryHandler, CommandHandler, ContextTypes

from core.config import TOKEN
from service.bill import daily_bill_remind_job
from service.callback_router import callback_router


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send bill message."""
    user_id = update.effective_chat.id

    context.job_queue.run_once(daily_bill_remind_job, when=timedelta(seconds=1), user_id=user_id)


def main() -> None:
    """Run the bot."""
    application = Application.builder().token(TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(callback_router))
    application.run_polling()


if __name__ == "__main__":
    main()
