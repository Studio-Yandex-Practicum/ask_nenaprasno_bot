from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import CallbackQueryHandler, CommandHandler, ContextTypes

from constants import command_constants
from core.config import URL_SERVICE_RULES


async def menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    menu_buttons = [
        [
            InlineKeyboardButton(
                text="⌚ Настроить часовой пояс", callback_data=command_constants.TIMEZONE_CONFIGURATE_COMMAND
            )
        ],
        [
            InlineKeyboardButton(text="📊 Статистика за месяц", callback_data=command_constants.STATISTIC_MONTH_COMMAND),
        ],
        [InlineKeyboardButton(text="📈 Статистика за неделю", callback_data=command_constants.STATISTIC_WEEK_COMMAND)],
        [InlineKeyboardButton(text="📌 В работе", callback_data=command_constants.ACTUAL_REQUESTS_COMMAND)],
        [InlineKeyboardButton(text="🔥 сроки горят", callback_data=command_constants.OVERDUE_REQUESTS_COMMAND)],
        [
            InlineKeyboardButton(
                text="📜 Правила сервиса",
                url=URL_SERVICE_RULES,
            )
        ],
    ]
    await update.message.reply_text("Меню", reply_markup=InlineKeyboardMarkup(menu_buttons))


async def handling_menu_button_click_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    await query.edit_message_text(query.data)


menu_command_handler = CommandHandler(command_constants.MENU_COMMAND, callback=menu)
callback_menu_handler = CallbackQueryHandler(handling_menu_button_click_callback)
