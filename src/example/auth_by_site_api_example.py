from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, PicklePersistence

from service.auth_procedure import auth_telegram_user
from src.core.config import TOKEN


async def get_from_persistence(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_name = context.user_data.get("user_name")
    user_id_in_trello = context.user_data.get("user_id_in_trello")
    user_time_zone = context.user_data.get("user_time_zone")
    if not user_name and not user_id_in_trello and not user_time_zone:
        await update.message.reply_text("bot don't have the data in persistence")
    else:
        await update.message.reply_text(
            f"user_data: {user_name}\nuser_id_in_trello: {user_id_in_trello}\nuser_time_zone: {user_time_zone}"
        )


async def push_to_persistence(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.message.from_user.id
    done = await auth_telegram_user(telegram_id=user_id, context=context)
    if done:
        await update.message.reply_text("Succeed get data from site api and write to persistence file")
    else:
        await update.message.reply_text("Something went wrong")


def main() -> None:
    """Run the bot."""
    bot_persistence = PicklePersistence(filepath="test_persistence_file")
    application = ApplicationBuilder().token(TOKEN).persistence(persistence=bot_persistence).build()
    application.add_handler(CommandHandler("get", get_from_persistence))
    application.add_handler(CommandHandler("push", push_to_persistence))
    application.run_polling()


if __name__ == "__main__":
    main()
