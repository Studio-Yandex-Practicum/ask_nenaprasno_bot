from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import CallbackContext

from core.config import MAIN_URL

MENU_BUTTONS = [
    [
        InlineKeyboardButton(
            text='⌚ Настройка временной зоны', callback_data='Actual requests'
        )
    ],
    [
        InlineKeyboardButton(
            text='📊 Статистика за месяц', callback_data='Month statistic'
        ),
    ],
    [
        InlineKeyboardButton(
            text='📈 Статистика за неделю', callback_data='Week statistic'
        )
    ],
    [
        InlineKeyboardButton(
            text='📌 Заявки в работе', callback_data='Actual requests'
        )
    ],
[
        InlineKeyboardButton(
            text='⚠ Просроченные заявки', callback_data='Actual requests'
        )
    ],
    [InlineKeyboardButton(text='🖥 Перейти на сайт', url=MAIN_URL)],
]


REMINDER_BUTTONS = [
    [
        InlineKeyboardButton(
            text='🕑 Напомнить через час', callback_data='Hour remind'
        )
    ],
    [
        InlineKeyboardButton(
            text='👌 Скоро отправлю', callback_data='Soon'
        )
    ],
    [
        InlineKeyboardButton(
            text='✅ Уже отправил(а)', callback_data='Already send'
        )
    ]
]

request_inline_keyboard = InlineKeyboardMarkup(MENU_BUTTONS)
reminder_inline_keyboard = InlineKeyboardMarkup(REMINDER_BUTTONS)


async def menu(
        update: Update, context: CallbackContext
) -> None:
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Меню",
        reply_markup=request_inline_keyboard
    )


async def remind(
        update: Update, context: CallbackContext
) -> None:
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Как ваши дела?",
        reply_markup=request_inline_keyboard
    )
