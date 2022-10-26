from telegram import BotCommand
from telegram.ext import CallbackContext

from constants import commands
from texts.buttons import BTN_MENU2, BTN_START

COMMANDS_UNAUTHORIZED = (BotCommand(commands.START, BTN_START),)
COMMANDS = (
    BotCommand(commands.MENU, BTN_MENU2),
    *COMMANDS_UNAUTHORIZED,
)


async def menu_button(context: CallbackContext, command) -> None:
    await context.bot.set_my_commands(command)
