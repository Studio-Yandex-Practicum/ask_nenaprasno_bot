import datetime

import pytz
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (
    CallbackContext,
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    filters,
)
from timezonefinder import TimezoneFinder

from constants import callback_data, states
from core.config import URL_SERVICE_RULES
from core.send_message import send_message
from get_timezone import get_timezone, set_timezone
from service.api_client import APIService

TIME_ZONE = "UTC"


async def timezone_message_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Sends a message after a successful timezone installation.
    """
    await send_message(
        context=context,
        chat_id=update.effective_user.id,
        text="Вы настроили часовой пояс, теперь уведомления будут приходить в удобное время",
    )


async def get_timezone_from_location_callback(update: Update, context: CallbackContext):
    """
    Sets timezone by geolocation.
    """
    user_timezone = TimezoneFinder().timezone_at(
        lng=update.message.location.longitude, lat=update.message.location.latitude
    )
    if user_timezone is None:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="Не удалось определить часовой пояс. Пожалуйста, введите его вручную. Например: UTC+03:00",
        )
        return states.TIMEZONE_STATE
    time_zone = pytz.timezone(user_timezone)
    utc_time = datetime.datetime.utcnow()
    utc = float(time_zone.utcoffset(utc_time).total_seconds() / 3600)
    hours, minutes = divmod(utc * 60, 60)
    utc = f"{hours:+03.0f}:{minutes:02.0f}"
    text_utc = TIME_ZONE + utc
    await set_timezone(update.effective_chat.id, text_utc, context)
    await timezone_message_callback(update, context)
    return states.MENU_STATE


async def get_timezone_from_text_message_callback(update: Update, context: CallbackContext):
    """
    Sets timezone based on a text message from the user.
    """
    text = str(update.message.text)
    if text == "Напишу свою таймзону сам":
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="Введите таймзону UTC. Например: UTC+03:00",
        )
        return states.TIMEZONE_STATE
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="вы установили таймзону X",
    )
    await timezone_message_callback(update, context)
    return states.MENU_STATE


async def start(update: Update, context: CallbackContext):
    """
    Responds to the start command. The entry point to telegram bot.
    """
    keyboard = [
        [
            InlineKeyboardButton("Да", callback_data=callback_data.CALLBACK_IS_EXPERT_COMMAND),
            InlineKeyboardButton("Нет", callback_data=callback_data.CALLBACK_NOT_EXPERT_COMMAND),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        text="Привет! Этот бот предназаначен только для экспертов справочной службы Просто спросить. "
        "Вы являетесь экспертом?",
        reply_markup=reply_markup,
    )
    return states.UNAUTHORIZED_STATE


async def not_expert_callback(update: Update, context: CallbackContext):
    """
    Invites the user to become an expert.
    """
    keyboard = [
        [
            InlineKeyboardButton("Да", callback_data=callback_data.CALLBACK_REGISTR_AS_EXPERT_COMMAND),
            InlineKeyboardButton("Нет", callback_data=callback_data.CALLBACK_SUPPORT_OR_CONSULT_COMMAND),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.callback_query.message.reply_text(
        text="Этот бот предназначен только для экспертов справочной службы 'Просто спросить'. Хотите стать нашим "
        "экспертом и отвечать на заявки от пациентов и их близких?",
        reply_markup=reply_markup,
    )
    return states.REGISTRATION_STATE


async def support_or_consult_callback(update: Update, context: CallbackContext):
    """
    Offers to support the project.
    """
    await update.callback_query.message.reply_text(
        text="Наш Проект\nhttps://ask.nenaprasno.ru/\nподдержать нас можно здесь\nhttps://ask.nenaprasno.ru/#donation"
    )
    return ConversationHandler.END


async def registr_as_expert_callback(update: Update, context: CallbackContext):
    """
    Sends a registration form to the user.
    """
    await update.callback_query.message.reply_text(
        text="Мы всегда рады подключать к проекту новых специалистов! Здорово, что вы хотите работать с нами. "
        "Заполните, пожалуйста, эту анкету "
        "https://docs.google.com/forms/d/1GvlemFyhMyVy_Wf91NPYTAfD5717W44-Ge7HQ6ealA0/edit (нужно 15 минут). "
        "Команда сервиса подробно изучит вашу заявку и свяжется с вами в течение недели, чтобы договориться о "
        "видеоинтервью. Перед интервью мы можем попросить вас ответить на тестовый кейс, чтобы обсудить его на "
        "встрече. Желаем удачи :)"
    )
    return ConversationHandler.END


async def is_expert_callback(update: Update, context: CallbackContext):
    """
    try to authenticate telegram user on site API and write trello_id to persistence file
    """
    api_service = APIService()
    telegram_id = update.effective_user.id
    user_data = await api_service.authenticate_user(telegram_id=telegram_id)
    if user_data is None:
        await update.callback_query.edit_message_text(text="Ошибка авторизации")
        return states.UNAUTHORIZED_STATE
    context.user_data["user_name"] = user_data.user_name
    context.user_data["user_time_zone"] = user_data.user_time_zone
    await update.callback_query.edit_message_text(
        text=f"Авторизация прошла успешно\n" f"Добро пожаловать {user_data.user_name}"
    )
    await update.callback_query.message.reply_text(
        text="Вы успешно начали работу с ботом. Меня зовут Женя Краб, "
        "я telegram-bot для экспертов справочной службы "
        "'Просто спросить'. Я буду сообщать вам о новых заявках, "
        "присылать уведомления о новых сообщениях в чате от пациентов "
        "и их близких и напоминать о просроченных заявках. "
        "Нам нравится, что вы с нами. Не терпится увидеть вас в деле! "
        "Для начала, давайте настроим часовой пояс, чтобы вы получали "
        "уведомления в удобное время."
    )
    await update.callback_query.answer()
    await get_timezone(update, context)
    return states.TIMEZONE_STATE


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
    return states.MENU_STATE


async def configurate_timezone_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Makes the timezone setting.
    """
    await get_timezone(update, context)
    return states.TIMEZONE_STATE


async def statistic_month_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Sends monthly statistics to the user.
    """
    await update.callback_query.message.reply_text(text="statistic_month_callback")
    return states.MENU_STATE


async def statistic_week_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Sends weekly statistics to the user.
    """
    await update.callback_query.message.reply_text(text="statistic_week_callback")
    return states.MENU_STATE


async def actual_requests_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Sends a list of current requests/requests to the user.
    """
    await update.callback_query.message.reply_text(text="actual_requests_callback")
    return states.MENU_STATE


async def overdue_requests_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Sends to the user a list of overdue applications/requests or those that are running out of time.
    """
    await update.callback_query.message.reply_text(text="overdue_requests_callback")
    return states.MENU_STATE


start_command_handler = CommandHandler("start", start)
menu_command_handler = CommandHandler("menu", menu)
get_timezone_command_handler = CommandHandler("get_timezone", get_timezone)

authorized_user_command_handlers = (
    menu_command_handler,
    get_timezone_command_handler,
)


start_conversation = ConversationHandler(
    allow_reentry=True,
    persistent=True,
    name="start_conversation",
    entry_points=[start_command_handler],
    states={
        states.UNAUTHORIZED_STATE: [
            CallbackQueryHandler(is_expert_callback, pattern=callback_data.CALLBACK_IS_EXPERT_COMMAND),
            CallbackQueryHandler(not_expert_callback, pattern=callback_data.CALLBACK_NOT_EXPERT_COMMAND),
        ],
        states.REGISTRATION_STATE: [
            CallbackQueryHandler(registr_as_expert_callback, pattern=callback_data.CALLBACK_REGISTR_AS_EXPERT_COMMAND),
            CallbackQueryHandler(
                support_or_consult_callback, pattern=callback_data.CALLBACK_SUPPORT_OR_CONSULT_COMMAND
            ),
        ],
        states.TIMEZONE_STATE: [
            *authorized_user_command_handlers,
            MessageHandler(filters.LOCATION, get_timezone_from_location_callback),
            MessageHandler(filters.TEXT, get_timezone_from_text_message_callback),
        ],
        states.MENU_STATE: [
            *authorized_user_command_handlers,
            CallbackQueryHandler(
                configurate_timezone_callback, pattern=callback_data.CALLBACK_CONFIGURATE_TIMEZONE_COMMAND
            ),
            CallbackQueryHandler(statistic_month_callback, pattern=callback_data.CALLBACK_STATISTIC_MONTH_COMMAND),
            CallbackQueryHandler(statistic_week_callback, pattern=callback_data.CALLBACK_STATISTIC_WEEK_COMMAND),
            CallbackQueryHandler(actual_requests_callback, pattern=callback_data.CALLBACK_ACTUAL_REQUESTS_COMMAND),
            CallbackQueryHandler(overdue_requests_callback, pattern=callback_data.CALLBACK_OVERDUE_REQUESTS_COMMAND),
        ],
    },
    fallbacks=[],
)
