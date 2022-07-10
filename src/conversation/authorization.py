from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.constants import ParseMode
from telegram.ext import CallbackContext, CallbackQueryHandler, CommandHandler, ConversationHandler

from constants import callback_data, states
from conversation.menu import menu_conversation
from conversation.timezone import get_timezone, states_timezone_conversation_dict
from core import config
from core.logger import logger
from decorators.logger import async_error_logger
from menu_button import COMMANDS, COMMANDS_UNAUTHORIZED, menu_button
from service.api_client import APIService

SUCCESSFUL_AUTORIZATION_MESSAGE = (
    "Авторизация прошла успешно\n"
    "Добро пожаловать {user_name}"
)
BOT_GREETINGS_MESSAGE = (
    "Вы успешно начали работу с ботом. Меня зовут Женя Краб, "
    "я telegram-bot для экспертов справочной службы "
    "'Просто спросить'. Я буду сообщать вам о новых заявках, "
    "присылать уведомления о новых сообщениях в чате от пациентов "
    "и их близких и напоминать о просроченных заявках. "
    "Нам нравится, что вы с нами. Не терпится увидеть вас в деле! "
    "Для начала, давайте настроим часовой пояс, чтобы вы получали "
    "уведомления в удобное время."
)


@async_error_logger(name="conversation.authorization.start", logger=logger)
async def start(update: Update, context: CallbackContext):
    """
    Responds to the start command. The entry point to telegram bot.
    """
    user_data = await autorize_callback(update, context)

    if user_data != None:
        await update.message.reply_text(
            text=SUCCESSFUL_AUTORIZATION_MESSAGE
                .format(user_name=user_data.user_name)
        )
        await update.message.reply_text(
            text=BOT_GREETINGS_MESSAGE
        )
        await menu_button(context, COMMANDS)
        await get_timezone(update, context)
        return states.TIMEZONE_STATE

    await menu_button(context, COMMANDS_UNAUTHORIZED)
    keyboard = [
        [
            InlineKeyboardButton("Да", callback_data=callback_data.CALLBACK_IS_EXPERT_COMMAND),
            InlineKeyboardButton("Нет", callback_data=callback_data.CALLBACK_NOT_EXPERT_COMMAND),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        text="Привет! Этот бот предназначен только для экспертов справочной службы Просто спросить. "
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
            InlineKeyboardButton("Да", callback_data=callback_data.CALLBACK_REGISTER_AS_EXPERT_COMMAND),
            InlineKeyboardButton("Нет", callback_data=callback_data.CALLBACK_SUPPORT_OR_CONSULT_COMMAND),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.callback_query.edit_message_text(
        text="Этот бот предназначен только для экспертов справочной службы ***'Просто спросить'***.\n"
        "Хотите стать *нашим экспертом* 👨‍⚕️ и отвечать на заявки от пациентов и их близких?",
        reply_markup=reply_markup,
        parse_mode=ParseMode.MARKDOWN,
    )
    return states.REGISTRATION_STATE


@async_error_logger(name="conversation.authorization.support_or_consult_callback", logger=logger)
async def support_or_consult_callback(update: Update, context: CallbackContext):
    """
    Offers to support the project.
    """
    keyboard = [
        [
            InlineKeyboardButton("Получить онлайн консультацию", url=config.URL_SITE),
            InlineKeyboardButton("Поддержать проект", url=config.URL_SITE_DONATION),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.callback_query.edit_message_text(
        text='Этот бот предназначен только для экспертов справочной службы ***"Просто спросить"***.\n'
        "Если у вас возникли вопросы об онкологическом заболевании, "
        'заполните заявку на странице справочной службы ***"Просто спросить"***.',
        reply_markup=reply_markup,
        parse_mode=ParseMode.MARKDOWN,
    )
    return ConversationHandler.END


@async_error_logger(name="conversation.authorization.register_as_expert_callback", logger=logger)
async def register_as_expert_callback(update: Update, context: CallbackContext):
    """
    Sends a registration form to the user.
    """
    await update.callback_query.message.reply_text(
        text="Мы всегда рады подключать к проекту новых специалистов!\nЗдорово, что вы хотите работать с нами 🤗.\n"
        f"Заполните, пожалуйста, эту [анкету]({config.FORM_URL_FUTURE_EXPERT})  (нужно 15 минут).\n\n"
        "Команда сервиса подробно изучит вашу заявку и свяжется с вами в течение недели, чтобы договориться о "
        "видеоинтервью.\nПеред интервью мы можем попросить вас ответить на тестовый кейс, чтобы обсудить его на "
        "встрече.\n\nЖелаем удачи 😊",
        parse_mode=ParseMode.MARKDOWN,
    )
    return ConversationHandler.END


@async_error_logger(name="conversation.authorization.autorize_callback", logger=logger)
async def autorize_callback(update: Update, context: CallbackContext):
    """
    try to authenticate telegram user on site API
    """
    api_service = APIService()
    telegram_id = update.effective_user.id
    user_data = await api_service.authenticate_user(telegram_id=telegram_id)
    if user_data is not None:
        context.user_data["user_name"] = user_data.user_name
        context.user_data["user_time_zone"] = user_data.user_time_zone
        context.user_data["user_name_in_trello"] = user_data.user_name_in_trello
    return user_data


@async_error_logger(name="conversation.authorization.is_expert_callback", logger=logger)
async def is_expert_callback(update: Update, context: CallbackContext):
    """
    try to authenticate telegram user on site API and write trello_id to persistence file
    """
    user_data = await autorize_callback(update, context)

    if user_data == None:
        telegram_id = update.effective_user.id
        message = (
            f"Ваш Telegram-идентификатор - ```{telegram_id}```\n\n"
            f"Для дальнейшей работы, пожалуйста, перешлите это сообщение кейс-менеджеру, "
            f"чтобы начать получать уведомления."
        )
        await update.callback_query.edit_message_text(text=message, parse_mode=ParseMode.MARKDOWN)
        return states.UNAUTHORIZED_STATE

    await update.callback_query.edit_message_text(
        text=SUCCESSFUL_AUTORIZATION_MESSAGE
            .format(user_name=user_data.user_name)
    )
    await update.callback_query.message.reply_text(
        text=BOT_GREETINGS_MESSAGE
    )
    await menu_button(context, COMMANDS)
    await get_timezone(update, context)
    return states.TIMEZONE_STATE


authorization_conversation = ConversationHandler(
    allow_reentry=True,
    persistent=True,
    name="authorization_conversation",
    entry_points=[
        CommandHandler("start", start),
    ],
    states={
        states.UNAUTHORIZED_STATE: [
            CallbackQueryHandler(is_expert_callback, pattern=callback_data.CALLBACK_IS_EXPERT_COMMAND),
            CallbackQueryHandler(not_expert_callback, pattern=callback_data.CALLBACK_NOT_EXPERT_COMMAND),
        ],
        states.REGISTRATION_STATE: [
            CallbackQueryHandler(
                register_as_expert_callback, pattern=callback_data.CALLBACK_REGISTER_AS_EXPERT_COMMAND
            ),
            CallbackQueryHandler(
                support_or_consult_callback, pattern=callback_data.CALLBACK_SUPPORT_OR_CONSULT_COMMAND
            ),
        ],
        states.MENU_STATE: [menu_conversation],
        **states_timezone_conversation_dict,
    },
    fallbacks=[],
)
