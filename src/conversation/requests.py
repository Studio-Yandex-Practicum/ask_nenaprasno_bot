from telegram import Update
from telegram.ext import CallbackQueryHandler, CommandHandler, ContextTypes

from constants import callback_data, commands, states


async def actual_requests_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Sends a list of current requests/requests to the user.
    """
    await update.callback_query.message.reply_text(text="actual_requests_callback")
    return states.BASE_STATE


async def overdue_requests_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Sends to the user a list of overdue applications/requests or those that are running out of time.
    """
    await update.callback_query.message.reply_text(text="overdue_requests_callback")
    return states.BASE_STATE


actual_requests_callback_handler = CallbackQueryHandler(
    actual_requests_callback, pattern=callback_data.CALLBACK_ACTUAL_REQUESTS_COMMAND
)
overdue_requests_callback_handler = CallbackQueryHandler(
    overdue_requests_callback, pattern=callback_data.CALLBACK_OVERDUE_REQUESTS_COMMAND
)


async def actual_requests(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Sends a list of current requests/requests to the user.
    """
    await update.message.reply_text(text="actual_requests_command")
    return states.BASE_STATE


async def overdue_requests(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Sends to the user a list of overdue applications/requests or those that are running out of time.
    """
    await update.message.reply_text(text="overdue_requests_command")
    return states.BASE_STATE


actual_requests_command_handler = CommandHandler(commands.STATEMENTS, actual_requests)
overdue_requests_command_handler = CommandHandler(commands.DEADLINES, overdue_requests)
