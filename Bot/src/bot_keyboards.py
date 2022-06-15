from telegram import InlineKeyboardButton, InlineKeyboardMarkup

from core.config import MAIN_URL

request_buttons = [
    [
        InlineKeyboardButton(
            text='Текущие заявки', callback_data='Actual requests'
        )
    ],
    [
        InlineKeyboardButton(
            text='Статистика за месяц', callback_data='Month statistic'
        ),
        InlineKeyboardButton(
            text='Статистика за неделю', callback_data='Week statistic'
        )
    ],
    [InlineKeyboardButton(text='Перейти на сайт', url=MAIN_URL)],
]

reminder_buttons = [
    [
        InlineKeyboardButton(
            text='Напомнить через час', callback_data='Month statistic'
        )
    ],
    [
        InlineKeyboardButton(
            text='Скоро отправлю', callback_data='Actual requests'
        )
    ],
    [
        InlineKeyboardButton(
            text='Уже отправил(а)', callback_data='Week statistic'
        )
    ]
]

request_inline_keyboard = InlineKeyboardMarkup(request_buttons)
reminder_inline_keyboard = InlineKeyboardMarkup(reminder_buttons)
