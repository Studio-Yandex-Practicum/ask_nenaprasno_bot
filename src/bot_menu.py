from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import CommandHandler, ContextTypes, CallbackQueryHandler

from constants import command_constants


remind_one_hour_button = InlineKeyboardButton(
    text='🕑 Напомнить через час',
    callback_data=command_constants.COMMAND_HOUR_REMIND
)
bill_keyboard = InlineKeyboardMarkup([
    [remind_one_hour_button],
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
])
remind_keyboard = InlineKeyboardMarkup([[remind_one_hour_button]])


async def menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    menu_buttons = [
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
    await update.message.reply_text(
        "Меню", reply_markup=InlineKeyboardMarkup(menu_buttons)
    )


async def handling_menu_button_click(
        update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    """Parses the CallbackQuery and updates the message text."""
    query = update.callback_query
    await query.answer()
    await query.edit_message_text(query.data)


menu_handler = CommandHandler('menu', callback=menu)
callback_menu_handler = CallbackQueryHandler(handling_menu_button_click)
