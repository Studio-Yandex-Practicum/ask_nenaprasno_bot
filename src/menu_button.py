from telegram import BotCommand
from telegram.ext import CallbackContext


async def menu_button(context: CallbackContext) -> None:
    command = [
        BotCommand("menu", "Показать список возможных запросов к боту"),
    ]
    await context.bot.set_my_commands(command)
