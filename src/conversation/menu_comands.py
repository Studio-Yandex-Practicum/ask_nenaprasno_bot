from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import CallbackQueryHandler, CommandHandler, ContextTypes, ConversationHandler

from constants import callback_data, states
from core.config import URL_SERVICE_RULES
from conversation.timezone import get_timezone, states_timezone_conversation_dict, timezone_command_handler

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


async def statistic_month_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Sends monthly statistics to the user.
    """
    await update.callback_query.message.reply_text(text="statistic_month_callback")
    return states.BASE_STATE


async def statistic_week_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Sends weekly statistics to the user.
    """
    await update.callback_query.message.reply_text(text="statistic_week_callback")
    return states.BASE_STATE


async def actual_requests_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Sends a list of current requests/requests to the user.
    """
    await update.callback_query.message.reply_text(text="actual_requests_callback")
    return states.BASE_STATE


async def overdue_requests_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Sends to the user a list of overdue applications/requests or those that are running out of time.
    """
    await update.callback_query.message.reply_text(text="overdue_requests_callback")
    return states.BASE_STATE


menu_command_handler = CommandHandler("menu", menu)

authorized_user_command_handlers = (
    menu_command_handler,
    timezone_command_handler,
)


menu_conversation = ConversationHandler(
    allow_reentry=True,
    persistent=True,
    name="menu_conversation",
    entry_points=[menu_command_handler],
    states={
        states.BASE_STATE: [
            *authorized_user_command_handlers,
            CallbackQueryHandler(get_timezone, pattern=callback_data.CALLBACK_CONFIGURATE_TIMEZONE_COMMAND),
            CallbackQueryHandler(statistic_month_callback, pattern=callback_data.CALLBACK_STATISTIC_MONTH_COMMAND),
            CallbackQueryHandler(statistic_week_callback, pattern=callback_data.CALLBACK_STATISTIC_WEEK_COMMAND),
            CallbackQueryHandler(actual_requests_callback, pattern=callback_data.CALLBACK_ACTUAL_REQUESTS_COMMAND),
            CallbackQueryHandler(overdue_requests_callback, pattern=callback_data.CALLBACK_OVERDUE_REQUESTS_COMMAND),
        ],
        **states_timezone_conversation_dict,
    },
    fallbacks=[],
    map_to_parent={
        states.END_STATE: states.BASE_STATE
    }
)
