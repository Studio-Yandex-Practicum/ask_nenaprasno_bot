from telegram import BotCommand
from telegram.ext import CallbackContext

from constants import commands

COMMANDS_UNAUTHORIZWD = (
    BotCommand(commands.START, "start"),
    BotCommand(commands.STOP, "stop"),
    BotCommand(commands.SERVICE_POLICE, "pravila"),
)
COMMANDS = (
    BotCommand(commands.STATISTIC, "stat"),
    BotCommand(commands.MENU, "menu"),
    BotCommand(commands.GET_TIMEZONE, "get_timezone"),
    BotCommand(commands.DEADLINES, "srok"),
    BotCommand(commands.STATEMENTS, "zayavki"),
    *COMMANDS_UNAUTHORIZWD
)


async def menu_button(context: CallbackContext, command) -> None:
    await context.bot.set_my_commands(command)
