from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import CommandHandler, ContextTypes, CallbackQueryHandler

from constants import command_constants


MENU_BUTTONS = [
    [
        InlineKeyboardButton(
            text='⌚ Настройка временной зоны',
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
            text='📌 Заявки в работе',
            callback_data=command_constants.COMMAND_ACTUAL_REQUESTS
        )
    ],
[
        InlineKeyboardButton(
            text='⚠ Просроченные заявки',
            callback_data=command_constants.COMMAND_OVERDUE_REQUESTS
        )
    ],
]

remind_one_hour = InlineKeyboardButton(
    text='🕑 Напомнить через час',
    callback_data=command_constants.COMMAND_HOUR_REMIND
)

send_check_reactions = [
    [remind_one_hour],
    [
        InlineKeyboardButton(
            text='👌 Скоро отправлю',
            callback_data=command_constants.COMMAND_SEND_SOON
        )
    ],
    [
        InlineKeyboardButton(
            text='✅ Уже отправил(а)',
            callback_data=command_constants.COMMAND_ALREADY_SEND
        )
    ]
]

request_inline_keyboard = InlineKeyboardMarkup(MENU_BUTTONS)
reminder_inline_keyboard = InlineKeyboardMarkup(send_check_reactions)


async def menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "Меню", reply_markup=request_inline_keyboard
    )


async def button(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Parses the CallbackQuery and updates the message text."""
    query = update.callback_query
    await query.answer()

menu_handler = CommandHandler('menu', callback=menu)
callback_menu_handler = CallbackQueryHandler(button)
