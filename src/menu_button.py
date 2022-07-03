from telegram import BotCommand
from telegram.ext import CallbackContext

from constants import commands

COMMANDS_UNAUTHORIZWD = (
    BotCommand(commands.START, "Начать работу с ботом."),
    BotCommand(commands.STOP, "Остановить бот."),
    BotCommand(commands.SERVICE_POLICE, "Правила сервиса."),
)
COMMANDS = (
    BotCommand(commands.STATISTIC, "Посмотреть свою статистику."),
    BotCommand(commands.MENU, "Показать список возможных запросов."),
    BotCommand(commands.GET_TIMEZONE, "Установить часовой пояс."),
    BotCommand(commands.DEADLINES, "Количество просроченных заявок."),
    BotCommand(commands.STATEMENTS, "Количество заявок в работе."),
    *COMMANDS_UNAUTHORIZWD
)


async def menu_button(context: CallbackContext, command) -> None:
    await context.bot.set_my_commands(command)
