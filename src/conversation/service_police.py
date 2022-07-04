from telegram import Update
from telegram.ext import CommandHandler, ContextTypes

from constants import commands, states
from core.config import URL_SERVICE_RULES
from core.logger import logger
from decorators.logger import async_error_logger


@async_error_logger(name="conversation.service_police.service_police", logger=logger)
async def service_police(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Makes the timezone setting.
    """
    await update.message.reply_html(text=URL_SERVICE_RULES)
    return states.END_STATE


service_police_command_handler = CommandHandler(commands.SERVICE_POLICE, service_police)
