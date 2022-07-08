from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import CallbackQueryHandler, CommandHandler, ContextTypes, ConversationHandler

from constants import callback_data, states
from conversation.timezone import get_timezone as configurate_timezone
from conversation.timezone import states_timezone_conversation_dict
from core.config import URL_SERVICE_RULES
from core.logger import logger
from decorators.logger import async_error_logger
from service.api_client import APIService


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


@async_error_logger(name="conversation.requests.actual_requests_callback", logger=logger)
async def button_reaction_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Sends a list of current requests/requests to the user.
    """
    await update.callback_query.message.reply_text(text="button_reaction_callback")
    return states.BASE_STATE


@async_error_logger(name="conversation.requests.button_statistic_moth_callback", logger=logger)
async def button_statistic_month_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Send monthly statistics at the user's request.
    """
    service = APIService()
    telegram_id = update.effective_user.id
    user_statistic = await service.get_user_month_stat(telegram_id=telegram_id)
    message = (
        f"❗Cтатистика за месяц❗ \n\n"
        f"✅Количество закрытых заявок - {user_statistic.user_tickets_closed}\n"
        f"✅Рейтинг - {user_statistic.user_rating}\n"
        f"✅Среднее время ответа - {user_statistic.user_ticket_resolve_avg_time}\n\n"
        f"Открыть [Trello](https://trello.com)\n\n"
    )
    await update.callback_query.message.reply_text(text=message)
    return states.BASE_STATE


menu_conversation = ConversationHandler(
    allow_reentry=True,
    persistent=True,
    name="menu_conversation",
    entry_points=[CommandHandler("menu", menu)],
    states={
        states.BASE_STATE: [
            CallbackQueryHandler(
                button_statistic_month_callback, pattern=callback_data.CALLBACK_STATISTIC_MONTH_COMMAND
            ),
            CallbackQueryHandler(button_reaction_callback, pattern=callback_data.CALLBACK_STATISTIC_WEEK_COMMAND),
            CallbackQueryHandler(button_reaction_callback, pattern=callback_data.CALLBACK_ACTUAL_REQUESTS_COMMAND),
            CallbackQueryHandler(button_reaction_callback, pattern=callback_data.CALLBACK_OVERDUE_REQUESTS_COMMAND),
            CallbackQueryHandler(configurate_timezone, pattern=callback_data.CALLBACK_CONFIGURATE_TIMEZONE_COMMAND),
        ],
        **states_timezone_conversation_dict,
    },
    fallbacks=[],
)
