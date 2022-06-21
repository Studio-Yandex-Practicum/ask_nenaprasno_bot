from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import CallbackQueryHandler, CommandHandler, ContextTypes

from constants import command_constants
from core.config import URL_SERVICE_RULES


async def menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    menu_buttons = [
        [
            InlineKeyboardButton(
                text='⌚ Настроить часовой пояс',
                callback_data=command_constants.COMMAND_TIMEZONE_CONFIGURATE
            )
        ],
        [
            InlineKeyboardButton(
                text='📊 Статистика за месяц',
                callback_data=command_constants.COMMAND_STATISTIC_MONTH
            ),
        ],
        [
            InlineKeyboardButton(
                text='📈 Статистика за неделю',
                callback_data=command_constants.COMMAND_STATISTIC_WEEK
            )
        ],
        [
            InlineKeyboardButton(
                text='📌 В работе',
                callback_data=command_constants.COMMAND_ACTUAL_REQUESTS
            )
        ],
        [
            InlineKeyboardButton(
                text='🔥 сроки горят',
                callback_data=command_constants.COMMAND_OVERDUE_REQUESTS
            )
        ],
        [
            InlineKeyboardButton(
                text='📜 Правила сервиса',
                url=URL_SERVICE_RULES,
            )
        ],
    ]
    await update.message.reply_text(
        "Меню", reply_markup=InlineKeyboardMarkup(menu_buttons)
    )


async def handling_menu_button_click_callback(
        update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    query = update.callback_query
    await query.answer()
    await query.edit_message_text(query.data)


menu_command_handler = CommandHandler(
    command_constants.COMMAND_MENU, callback=menu
)
callback_menu_handler = CallbackQueryHandler(
    handling_menu_button_click_callback
)
