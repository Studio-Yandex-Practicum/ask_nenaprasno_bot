from telegram import Update
from telegram.ext import CommandHandler, ContextTypes, PicklePersistence, ApplicationBuilder

from core.send_message import send_message
from service.auth_procedure import auth_telegram_user
from src.core.config import TOKEN


async def get_from_persistance(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.message.from_user.id
    user_data = context.user_data["user_name"]
    await update.message.reply_text(f"try get data from persistence of {user_data}")


async def push_to_persistance(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.message.from_user.id
    await auth_telegram_user(
        telegram_id=user_id,
        context=context
    )
    await update.message.reply_text(f"try push data to persistence of {user_id}")


def main() -> None:
    """Run the bot."""

    bot_persistence = PicklePersistence(filepath="test_persistence_file")
    application = ApplicationBuilder().token(TOKEN).persistence(persistence=bot_persistence).build()
    application.add_handler(CommandHandler("get", get_from_persistance))
    application.add_handler(CommandHandler("push", push_to_persistance))
    application.run_polling()


if __name__ == "__main__":
    main()
