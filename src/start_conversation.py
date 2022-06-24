from telegram import (InlineKeyboardButton, InlineKeyboardMarkup,
                      ReplyKeyboardRemove, Update)
from telegram.ext import (CallbackQueryHandler, ConversationHandler,
                          CommandHandler, ContextTypes, CallbackContext)

from constants import command_constans as cmd_const, states


async def start(update: Update, context: CallbackContext):
    keyboard = [
        [
            InlineKeyboardButton(
                "Да",
                callback_data=cmd_const.COMMAND_IS_EXPERT
            ),
            InlineKeyboardButton(
                "Нет",
                callback_data=cmd_const.COMMAND_NOT_EXPERT
            ),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        text="Привет! Этот бот предназаначен только для"
             "экспертов справочной службы Просто спросить."
             "Вы являетесь экспертом?",
        reply_markup=reply_markup)
    return states.UNAUTHORIZED_STATE


async def not_expert_callback(update: Update, context: CallbackContext):
    keyboard = [
        [
            InlineKeyboardButton(
                "Да",
                callback_data=cmd_const.COMMAND_REGISTR_EXPERT
            ),
            InlineKeyboardButton(
                "Нет",
                callback_data=cmd_const.COMMAND_SUPPORT_OR_CONSULT
            ),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        text="Этот бот предназаначен только для"
             "экспертов справочной службы 'Просто спросить'."
             "Хотите стать нашим экспертом и отвечать на заявки"
             "от пациентов и их близких?",
        reply_markup=reply_markup)
    return states.REGISTRATION_STATE


async def support_or_consult_callback(
    update: Update,
    context: CallbackContext
):
    return ConversationHandler.END


async def registr_as_expert_callback(update: Update, context: CallbackContext):
    await update.message.reply_text(
        text="Мы всегда рады подключать к проекту новых специалистов!"
             "Здорово, что вы хотите работать с нами. Заполните,"
             "пожалуйста, эту анкету (нужно 15 минут). Команда сервиса"
             "подробно изучит вашу заявку и свяжется с вами в течение недели,"
             "чтобы договориться о видеоинтервью."
             "Перед интервью мы можем попросить вас ответить на тестовый кейс,"
             "чтобы обсудить его на встрече. Желаем удачи :)"
    )
    return states.NEW_EXPERT_STATE


async def after_registr_message_callback(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):
    await update.message.reply_text(
        text="Вы успешно начали работу с ботом. Меня зовут Женя Краб,"
             "я telegram-bot для экспертов справочной службы"
             "'Просто спросить'. Я буду сообщать вам о новых заявках,"
             "присылать уведомления о новых сообщениях в чате от пациентов"
             "и их близких и напоминать о просроченных заявках."
             "Нам нравится, что вы с нами. Не терпится увидеть вас в деле!"
             "Для начала, давайте настроим часовой пояс, чтобы вы получали"
             "уведомления в удобное время."
    )
    return states.TIMEZONE_STATE


async def is_expert_callback(update: Update, context: CallbackContext):
    return states.TIMEZONE_STATE


async def timezone_callback(update: Update, context: CallbackContext):
    return states.MENU_STATE


async def skip_timezone_callback(update: Update, context: CallbackContext):
    return states.MENU_STATE


async def timezone_message_callback(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):
    await update.message.reply_text(
        text="Вы настроили часовой пояс,"
             "теперь уведомления будут приходить"
             "в удобное время",
        reply_markup=ReplyKeyboardRemove()
    )
    return ConversationHandler.END


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        text="Хьюстон, у нас проблемы. Что-то пошло не так",
        reply_markup=ReplyKeyboardRemove()
    )
    ConversationHandler.END


start_command_handler = CommandHandler("start", start)
cancel_command_handler = CommandHandler("cancel", cancel)

start_conversation = ConversationHandler(
    allow_reentry=True,
    persistent=True,
    name="start_conversation",
    entry_points=[start_command_handler],
    states={
        states.UNAUTHORIZED_STATE: [
            CallbackQueryHandler(
                is_expert_callback,
                pattern=cmd_const.COMMAND_IS_EXPERT
            ),
            CallbackQueryHandler(
                not_expert_callback,
                pattern=cmd_const.COMMAND_NOT_EXPERT
            )
        ],
        states.REGISTRATION_STATE: [
            CallbackQueryHandler(
                registr_as_expert_callback,
                pattern=cmd_const.COMMAND_REGISTR_EXPERT
            ),
            CallbackQueryHandler(
                support_or_consult_callback,
                pattern=cmd_const.COMMAND_SUPPORT_OR_CONSULT
            )
        ],
        states.NEW_EXPERT_STATE: [
            CallbackQueryHandler(after_registr_message_callback)
        ],
        states.TIMEZONE_STATE: [
            CallbackQueryHandler(
                timezone_callback,
                pattern=cmd_const.COMMAND_TIMEZONE
            ),
            CallbackQueryHandler(
                skip_timezone_callback,
                pattern=cmd_const.COMMAND_SKIP_TIMEZONE
            ),
            CallbackQueryHandler(timezone_message_callback)
        ],
        states.MENU_STATE: [],
    },
    fallbacks=[cancel_command_handler]
)
