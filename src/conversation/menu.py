from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import CallbackQueryHandler, CommandHandler, ContextTypes, ConversationHandler

from constants import callback_data, states
from conversation.timezone import get_timezone as configurate_timezone
from conversation.timezone import states_timezone_conversation_dict
from core.config import URL_SERVICE_RULES
from core.logger import logger
from decorators.logger import async_error_logger
from service.repeat_message import repeat_message_after_1_hour_callback


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


async def done_bill_callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Delete job from JobQueue
    """
    query = update.callback_query
    user_id = query.from_user.id
    current_jobs = context.job_queue.get_jobs_by_name(f"send_{user_id}_bill_until_complete")
    for job in current_jobs:
        job.schedule_removal()
    await query.edit_message_text(text="Не будем напоминать до следующего месяца")
    await query.answer()  # close progress bar in chat


async def skip_bill_callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Delete button under message"""
    query = update.callback_query
    data = query.message
    await query.edit_message_text(text=data.text_markdown_v2_urled)
    await query.answer()  # close progress bar in chat


menu_conversation = ConversationHandler(
    allow_reentry=True,
    persistent=True,
    name="menu_conversation",
    entry_points=[CommandHandler("menu", menu)],
    states={
        states.BASE_STATE: [
            CallbackQueryHandler(button_reaction_callback, pattern=callback_data.CALLBACK_STATISTIC_MONTH_COMMAND),
            CallbackQueryHandler(button_reaction_callback, pattern=callback_data.CALLBACK_STATISTIC_WEEK_COMMAND),
            CallbackQueryHandler(button_reaction_callback, pattern=callback_data.CALLBACK_ACTUAL_REQUESTS_COMMAND),
            CallbackQueryHandler(button_reaction_callback, pattern=callback_data.CALLBACK_OVERDUE_REQUESTS_COMMAND),
            CallbackQueryHandler(configurate_timezone, pattern=callback_data.CALLBACK_CONFIGURATE_TIMEZONE_COMMAND),
            CallbackQueryHandler(repeat_message_after_1_hour_callback, pattern=callback_data.CALLBACK_REPEAT_COMMAND),
            CallbackQueryHandler(done_bill_callback_handler, pattern=callback_data.CALLBACK_DONE_BILL_COMMAND),
            CallbackQueryHandler(skip_bill_callback_handler, pattern=callback_data.CALLBACK_SKIP_BILL_COMMAND),
        ],
        **states_timezone_conversation_dict,
    },
    fallbacks=[],
)
