from telegram.ext import CommandHandler

from src.user_conversation import start, open_menu

START_COMMAND_HANDLER = CommandHandler('start', start)
MENU_COMMAND_HANDLER = CommandHandler('menu', open_menu)
COMMAND_USER_IS_EXPERT = 'user_is_expert'
COMMAND_TIMEZONE = 'timezone'
COMMAND_SKIP_TIMEZONE = 'skip_timezone'
