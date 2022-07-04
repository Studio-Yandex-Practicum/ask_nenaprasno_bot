from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import CallbackContext, CallbackQueryHandler, CommandHandler, ConversationHandler

from constants import callback_data, states
from conversation.menu_commands import menu_conversation
from conversation.service_police import service_police_command_handler
from conversation.timezone import get_timezone, states_timezone_conversation_dict
from core.logger import logger
from decorators.logger import async_error_logger
from menu_button import COMMANDS, COMMANDS_UNAUTHORIZWD, menu_button
from service.api_client import APIService


@async_error_logger(name="conversation.authorization.start", logger=logger)
async def start(update: Update, context: CallbackContext):
    """
    Responds to the start command. The entry point to telegram bot.
    """
    await menu_button(context, COMMANDS_UNAUTHORIZWD)
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


@async_error_logger(name="conversation.authorization.not_expert_callback", logger=logger)
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


@async_error_logger(name="conversation.authorization.support_or_consult_callback", logger=logger)
async def support_or_consult_callback(update: Update, context: CallbackContext):
    """
    Offers to support the project.
    """
    await update.callback_query.message.reply_text(
        text="Наш Проект\nhttps://ask.nenaprasno.ru/\nподдержать нас можно здесь\nhttps://ask.nenaprasno.ru/#donation"
    )
    return ConversationHandler.END


@async_error_logger(name="conversation.authorization.registr_as_expert_callback", logger=logger)
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


@async_error_logger(name="conversation.authorization.is_expert_callback", logger=logger)
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
    await menu_button(context, COMMANDS)
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


authorization_conversation = ConversationHandler(
    allow_reentry=True,
    persistent=True,
    name="authorization_conversation",
    entry_points=[
        CommandHandler("start", start),
        service_police_command_handler,
    ],
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
        states.BASE_STATE: [menu_conversation],
        **states_timezone_conversation_dict,
    },
    fallbacks=[],
)
