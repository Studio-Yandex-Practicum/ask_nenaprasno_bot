from telegram import Update
from telegram.ext import (ApplicationBuilder, CommandHandler,
                          ContextTypes,CallbackContext, ConversationHandler,
                          MessageHandler, filters)
from constants import CHOOSING, MENU, START_COMMAND_HANDLER


async def user_is_expert_confirm(update: Update, context: CallbackContext):
    """После старта пользователь указывает является ли экспертом."""
    pass

async def user_is_not_expert(update: Update, context: CallbackContext):
    """Пользователь не является экспертом, предлагаем им стать."""
    pass

async def new_request_confirm(update: Update, context: CallbackContext):
    """Присылает сообщение о новых заявках."""
    return open_menu

async def open_menu(update: Update, context: CallbackContext):
    """Выводит меню."""
    return MENU


conv_handler = ConversationHandler(
    allow_reentry=True,
    entry_points=[START_COMMAND_HANDLER],
    states={
        CHOOSING: [
            CallbackQueryHandler(user_is_expert_confirm),
            CallbackQueryHandler(user_is_not_expert),
            CallbackQueryHandler(new_request_confirm),
            CallbackQueryHandler(menu)
        ],
    },
    fallbacks=[START_COMMAND_HANDLER],
)
