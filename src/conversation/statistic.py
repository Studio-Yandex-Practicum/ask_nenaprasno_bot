from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import CallbackQueryHandler, CommandHandler, ContextTypes, ConversationHandler

from constants import callback_data, states, commands
from core.config import URL_SERVICE_RULES
from conversation.timezone import get_timezone, states_timezone_conversation_dict, timezone_command_handler


async def statistic_month_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Sends monthly statistics to the user.
    """
    await update.callback_query.message.reply_text(text="statistic_month_callback")
    return states.BASE_STATE


async def statistic_week_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Sends weekly statistics to the user.
    """
    await update.callback_query.message.reply_text(text="statistic_week_callback")
    return states.BASE_STATE


statistic_month_callback_handler = CallbackQueryHandler(
    statistic_month_callback, pattern=callback_data.CALLBACK_STATISTIC_MONTH_COMMAND
)
statistic_week_callback_handler = CallbackQueryHandler(
    statistic_week_callback, pattern=callback_data.CALLBACK_STATISTIC_WEEK_COMMAND
)


async def statistic(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Sends statistics to the user.
    """
    await update.message.reply_text(text="statistic_callback")
    return states.BASE_STATE

statistic_command_handler = CommandHandler(commands.STATISTIC, statistic)
