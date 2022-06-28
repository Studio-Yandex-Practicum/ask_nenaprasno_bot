from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import CallbackContext, CallbackQueryHandler, CommandHandler, ContextTypes, ConversationHandler

from constants import callback_data as callback
from constants import states
from core.config import URL_SERVICE_RULES
from core.send_message import send_message
from service import ConreateAPIService


async def start(update: Update, context: CallbackContext):
    keyboard = [
        [
            InlineKeyboardButton("Да", callback_data=callback.CALLBACK_IS_EXPERT_COMMAND),
            InlineKeyboardButton("Нет", callback_data=callback.CALLBACK_NOT_EXPERT_COMMAND),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        text="Привет! Этот бот предназаначен только для "
        "экспертов справочной службы Просто спросить. "
        "Вы являетесь экспертом?",
        reply_markup=reply_markup,
    )
    return states.UNAUTHORIZED_STATE


async def not_expert_callback(update: Update, context: CallbackContext):
    keyboard = [
        [
            InlineKeyboardButton("Да", callback_data=callback.CALLBACK_REGISTR_AS_EXPERT_COMMAND),
            InlineKeyboardButton("Нет", callback_data=callback.CALLBACK_SUPPORT_OR_CONSULT_COMMAND),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        text="Этот бот предназначен только для "
        "экспертов справочной службы 'Просто спросить'. "
        "Хотите стать нашим экспертом и отвечать на заявки "
        "от пациентов и их близких?",
        reply_markup=reply_markup,
    )
    return states.REGISTRATION_STATE


async def support_or_consult_callback(update: Update, context: CallbackContext):
    return ConversationHandler.END


async def registr_as_expert_callback(update: Update, context: CallbackContext):
    await update.message.reply_text(
        text="Мы всегда рады подключать к проекту новых специалистов! "
        "Здорово, что вы хотите работать с нами. Заполните, "
        "пожалуйста, эту анкету (нужно 15 минут). Команда сервиса "
        "подробно изучит вашу заявку и свяжется с вами в течение недели, "
        "чтобы договориться о видеоинтервью. "
        "Перед интервью мы можем попросить вас ответить на тестовый кейс, "
        "чтобы обсудить его на встрече. Желаем удачи :)"
    )
    return states.NEW_EXPERT_STATE


async def after_registr_message_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        text="Вы успешно начали работу с ботом. Меня зовут Женя Краб, "
        "я telegram-bot для экспертов справочной службы "
        "'Просто спросить'. Я буду сообщать вам о новых заявках, "
        "присылать уведомления о новых сообщениях в чате от пациентов "
        "и их близких и напоминать о просроченных заявках. "
        "Нам нравится, что вы с нами. Не терпится увидеть вас в деле! "
        "Для начала, давайте настроим часовой пояс, чтобы вы получали "
        "уведомления в удобное время."
    )
    return states.TIMEZONE_STATE


async def is_expert_callback(update: Update, context: CallbackContext):
    """
    try to authenticate telegram user on site API and write trello_id to persistence file
    """
    api_service = ConreateAPIService()
    telegram_id = update.effective_user.id
    user_data = await api_service.authenticate_user(telegram_id=telegram_id)
    if user_data is None:
        await update.callback_query.edit_message_text(text="Ошибка авторизации")
        return states.UNAUTHORIZED_STATE
    context.user_data["user_name"] = user_data.user_name
    context.user_data["user_id_in_trello"] = user_data.user_id_in_trello
    context.user_data["user_time_zone"] = user_data.user_time_zone
    await update.callback_query.edit_message_text(
        text=f"Авторизация прошла успешно\n" f"Добро пожаловать {user_data.user_name}"
    )
    await update.callback_query.answer()
    return states.TIMEZONE_STATE


async def timezone_callback(update: Update, context: CallbackContext):
    return states.MENU_STATE


async def skip_timezone_callback(update: Update, context: CallbackContext):
    return states.MENU_STATE


async def timezone_message_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await send_message(  # reply_message не работает
        context=context,
        chat_id=update.effective_user.id,
        text="Вы настроили часовой пояс, теперь уведомления будут приходить в удобное время",
    )
    return ConversationHandler.END


async def menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    menu_buttons = [
        [
            InlineKeyboardButton(
                text="⌚ Настроить часовой пояс", callback_data=callback.CALLBACK_CONFIGURATE_TIMEZONE_COMMAND
            )
        ],
        [
            InlineKeyboardButton(text="📊 Статистика за месяц", callback_data=callback.CALLBACK_STATISTIC_MONTH_COMMAND),
        ],
        [InlineKeyboardButton(text="📈 Статистика за неделю", callback_data=callback.CALLBACK_STATISTIC_WEEK_COMMAND)],
        [InlineKeyboardButton(text="📌 В работе", callback_data=callback.CALLBACK_ACTUAL_REQUESTS_COMMAND)],
        [InlineKeyboardButton(text="🔥 сроки горят", callback_data=callback.CALLBACK_OVERDUE_REQUESTS_COMMAND)],
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


start_command_handler = CommandHandler("start", start)
menu_command_handler = CommandHandler("menu", menu)

callback_menu_handler = CallbackQueryHandler(handling_menu_button_click_callback)

start_conversation = ConversationHandler(
    allow_reentry=True,
    persistent=True,
    name="start_conversation",
    entry_points=[start_command_handler, menu_command_handler],
    states={
        states.UNAUTHORIZED_STATE: [
            CallbackQueryHandler(is_expert_callback, pattern=callback.CALLBACK_IS_EXPERT_COMMAND),
            CallbackQueryHandler(not_expert_callback, pattern=callback.CALLBACK_NOT_EXPERT_COMMAND),
        ],
        states.REGISTRATION_STATE: [
            CallbackQueryHandler(registr_as_expert_callback, pattern=callback.CALLBACK_REGISTR_AS_EXPERT_COMMAND),
            CallbackQueryHandler(support_or_consult_callback, pattern=callback.CALLBACK_SUPPORT_OR_CONSULT_COMMAND),
        ],
        states.NEW_EXPERT_STATE: [CallbackQueryHandler(after_registr_message_callback)],
        states.TIMEZONE_STATE: [
            CallbackQueryHandler(timezone_callback, pattern=callback.CALLBACK_TIMEZONE_COMMAND),
            CallbackQueryHandler(skip_timezone_callback, pattern=callback.CALLBACK_SKIP_TIMEZONE_COMMAND),
            CallbackQueryHandler(timezone_message_callback),
        ],
        states.MENU_STATE: [callback_menu_handler],
    },
    fallbacks=[],
)
