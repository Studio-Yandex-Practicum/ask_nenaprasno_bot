from telegram import BotCommand
from telegram.ext import CallbackContext

from constants import commands
from texts import buttons as texts_buttons

COMMANDS_UNAUTHORIZED = (BotCommand(commands.START, texts_buttons.START),)
COMMANDS = (
    BotCommand(commands.MENU, texts_buttons.MENU2),
    *COMMANDS_UNAUTHORIZED,
)


async def menu_button(context: CallbackContext, command) -> None:
    await context.bot.set_my_commands(command)
