from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import CallbackQueryHandler, CommandHandler, ContextTypes, ConversationHandler

from constants import callback_data, states
from conversation.requests import (
    actual_requests_callback_handler,
    actual_requests_command_handler,
    overdue_requests_callback_handler,
    overdue_requests_command_handler,
)
from conversation.statistic import (
    statistic_command_handler,
    statistic_month_callback_handler,
    statistic_week_callback_handler,
)
from conversation.timezone import get_timezone as configurate_timezone
from conversation.timezone import states_timezone_conversation_dict, timezone_command_handler
from core.config import URL_SERVICE_RULES
from core.logger import logger
from decorators.logger import async_error_logger


@async_error_logger(name="conversation.menu_commands.menu", logger=logger)
async def menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Displays the menu.
    """
    menu_buttons = [
        [
            InlineKeyboardButton(
                text="⌚ Настроить часовой пояс", callback_data=callback_data.CALLBACK_CONFIGURATE_TIMEZONE_COMMAND
            )
        ],
        [
            InlineKeyboardButton(
                text="📊 Статистика за месяц", callback_data=callback_data.CALLBACK_STATISTIC_MONTH_COMMAND
            ),
        ],
        [
            InlineKeyboardButton(
                text="📈 Статистика за неделю", callback_data=callback_data.CALLBACK_STATISTIC_WEEK_COMMAND
            )
        ],
        [InlineKeyboardButton(text="📌 В работе", callback_data=callback_data.CALLBACK_ACTUAL_REQUESTS_COMMAND)],
        [InlineKeyboardButton(text="🔥 сроки горят", callback_data=callback_data.CALLBACK_OVERDUE_REQUESTS_COMMAND)],
        [
            InlineKeyboardButton(
                text="📜 Правила сервиса",
                url=URL_SERVICE_RULES,
            )
        ],
    ]
    await update.message.reply_text("Меню", reply_markup=InlineKeyboardMarkup(menu_buttons))
    return states.BASE_STATE


menu_command_handler = CommandHandler("menu", menu)

authorized_user_command_handlers = (
    menu_command_handler,
    timezone_command_handler,
    statistic_command_handler,
    actual_requests_command_handler,
    overdue_requests_command_handler,
)

menu_conversation = ConversationHandler(
    allow_reentry=True,
    persistent=True,
    name="menu_conversation",
    entry_points=[menu_command_handler],
    states={
        states.BASE_STATE: [
            *authorized_user_command_handlers,
            statistic_month_callback_handler,
            statistic_week_callback_handler,
            actual_requests_callback_handler,
            overdue_requests_callback_handler,
            CallbackQueryHandler(configurate_timezone, pattern=callback_data.CALLBACK_CONFIGURATE_TIMEZONE_COMMAND),
        ],
        **states_timezone_conversation_dict,
    },
    fallbacks=[],
    map_to_parent={ConversationHandler.END: states.BASE_STATE},
)
