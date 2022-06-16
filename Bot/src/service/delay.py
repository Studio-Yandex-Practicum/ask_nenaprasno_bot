# Use case
#
# Inline keyboard return some message after the push of a button.
# For delay button return some message, for example "delay"
# This message should be use as a pattern in CallbackQueryHandler
# CallbackQueryHandler(delay_message_for_1_hour, pattern="delay")

from datetime import timedelta

from telegram import Update
from telegram.ext import ContextTypes, CallbackContext


async def delay_message_for_1_hour(
        update: Update,
        context: ContextTypes.DEFAULT_TYPE
) -> None:
    """
    Add a repeat message task to the queue.
    """
    query = update.callback_query
    data = query.message
    context.job_queue.run_once(
        callback=repeat_message,
        when=timedelta(hours=1),
        data=data
    )
    await query.answer()  # close progress bar in chat


async def repeat_message(
        context: CallbackContext
) -> None:
    """
    Repeat delayed message.
    """
    data = context.job.data
    await context.bot.send_message(
        chat_id=data.chat_id,
        text=data.text_markdown_v2_urled,
        reply_markup=data.reply_markup
    )
