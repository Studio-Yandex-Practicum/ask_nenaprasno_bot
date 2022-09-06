# pylint: disable=import-error, wrong-import-position
import asyncio
import sys
from pathlib import Path

from telegram import Update
from telegram.ext import AIORateLimiter, Application, CommandHandler, ContextTypes

dir_code_of_bot = f"{Path(__file__).resolve().parent.parent}/src"
sys.path.append(dir_code_of_bot)

from core.config import TOKEN


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Checking the operation of the limit bypass function.
    Specificity: if you send several messages at once,
    the order of arrival of messages in the chat is not correct.
    """
    tasks = []
    for i in range(50):
        tasks.append(update.message.reply_text(text=f"Test - {i+1}"))
    await asyncio.gather(*tasks)


def main() -> None:
    """Run the bot."""
    application = Application.builder().token(TOKEN).rate_limiter(AIORateLimiter()).build()
    application.add_handler(CommandHandler("start", start))
    application.run_polling()


if __name__ == "__main__":
    main()
