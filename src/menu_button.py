from telegram import BotCommand
from telegram.ext import CallbackContext

from constants import commands

COMMANDS_UNAUTHORIZED = (BotCommand(commands.START, "Начать работу с ботом."),)
COMMANDS = (
    BotCommand(commands.MENU, "Показать список возможных запросов."),
    *COMMANDS_UNAUTHORIZED,
)


async def menu_button(context: CallbackContext, command) -> None:
    await context.bot.set_my_commands(command)
