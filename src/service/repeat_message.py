# Use case
#
# Inline keyboard return some message after the push of a button.
# For delay button return some message, for example "delay"
# This message should be use as a pattern in CallbackQueryHandler
# CallbackQueryHandler(delay_message_for_1_hour, pattern="delay")

from datetime import timedelta

from telegram import InlineKeyboardButton, Update
from telegram.ext import CallbackContext, ContextTypes

from constants.callback_data import CALLBACK_REPEAT_COMMAND
from core.send_message import edit_message, send_message


async def repeat_message_after_1_hour_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Add a repeat message task to the queue."""
    query = update.callback_query
    data = query.message
    context.job_queue.run_once(
        callback=repeat_message_job, when=timedelta(hours=1), data=data, chat_id=query.message.chat.id
    )
    await edit_message(update=update, new_text=data.text_markdown)
    await query.answer()  # close progress bar in chat


async def repeat_message_job(context: CallbackContext) -> None:
    """Repeat delayed message."""
    data = context.job.data
    await send_message(
        bot=context.bot, chat_id=context.job.chat_id, text=data.text_markdown, reply_markup=data.reply_markup
    )


repeat_after_one_hour_button = InlineKeyboardButton(text="🕑 Напомнить через час", callback_data=CALLBACK_REPEAT_COMMAND)
