from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import CallbackQueryHandler, CommandHandler, ContextTypes, ConversationHandler

from constants import callback_data, states
from conversation.timezone import get_timezone as configurate_timezone
from conversation.timezone import states_timezone_conversation_dict
from core.config import TRELLO_BORD_ID, URL_SERVICE_RULES, URL_SITE
from core.send_message import reply_message
from decorators.logger import async_error_logger
from service.api_client import APIService


@async_error_logger(name="conversation.menu_commands.menu")
async def menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Displays the menu.
    """
    menu_buttons = [
        [
            InlineKeyboardButton(
                text="Настроить часовой пояс", callback_data=callback_data.CALLBACK_CONFIGURATE_TIMEZONE_COMMAND
            )
        ],
        [
            InlineKeyboardButton(
                text="Статистика за месяц", callback_data=callback_data.CALLBACK_STATISTIC_MONTH_COMMAND
            ),
        ],
        [InlineKeyboardButton(text="В работе", callback_data=callback_data.CALLBACK_ACTUAL_REQUESTS_COMMAND)],
        [InlineKeyboardButton(text="🔥 Cроки горят", callback_data=callback_data.CALLBACK_OVERDUE_REQUESTS_COMMAND)],
        [
            InlineKeyboardButton(
                text="Правила сервиса",
                url=URL_SERVICE_RULES,
            )
        ],
    ]
    await reply_message(update=update, text="Меню", reply_markup=InlineKeyboardMarkup(menu_buttons))
    return states.MENU_STATE


@async_error_logger(name="conversation.requests.actual_requests_callback")
async def button_reaction_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Sends a list of current requests/requests to the user.
    """
    await reply_message(update=update, text="button reaction callback")
    return states.MENU_STATE


@async_error_logger(name="conversation.requests.button_statistic_month_callback")
async def button_statistic_month_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Send monthly statistics at the user's request.
    """
    service = APIService()
    telegram_id = update.effective_user.id
    user_statistics = await service.get_user_month_stat(telegram_id=telegram_id)
    if user_statistics.closed_consultations > 0:
        message = (
            f"С начала месяца вы сделали очень много для \"Просто спросить\" 🔥\n"
            f"***Количество закрытых заявок*** - {user_statistics.closed_consultations}\n"
            f"***Рейтинг*** - {user_statistics.rating:.1f}\n"
            f"***Среднее время ответа*** - {user_statistics.average_user_answer_time:.1f}\n\n"
            "Мы рады работать в одной команде :\\)\n"
            "Так держать!"
        )
    else:
        message = (
            "К сожалению у вас не было отвеченных завок :\\(\n"
            "Мы верим, что в следующем месяце все изменится! :\\)"
        )
    await reply_message(update=update, text=message)


@async_error_logger(name="conversation.requests.button_actual_requests_callback")
async def button_actual_requests_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Sends a list of active consultations to the user.
    """
    service = APIService()
    telegram_id = update.effective_user.id
    user_active_consultations = await service.get_user_active_consultations(telegram_id=telegram_id)
    consultations_list = user_active_consultations.active_consultations_data
    list_for_message = ""
    for consultation in consultations_list:
        list_for_message += f"{URL_SITE}doctor/consultation/{consultation['consultation_id']}\n"
    message = (
        f"У вас в работе {user_active_consultations.active_consultations} заявок.\n"
        f"Посмотреть заявки на сайте:\n{list_for_message}"
    )
    await reply_message(update=update, text=message)


@async_error_logger(name="conversation.requests.button_overdue_requests_callback")
async def button_overdue_requests_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Send information about expiring and overdue consultation
    """
    service = APIService()
    telegram_id = update.effective_user.id
    expired_consultations = await service.get_user_expired_consultations(telegram_id=telegram_id)
    expiring_consultations = await service.get_user_active_consultations(telegram_id=telegram_id)
    username_trello = expired_consultations.username_trello
    expired_consultations_list = expired_consultations.expired_consultations_data
    link_neneprasno = ""
    for consultation in expired_consultations_list:
        link_neneprasno += f"{URL_SITE}doctor/consultation/{consultation['consultation_id']}\n"
    message = (
        f"Время истекло 😎\n"
        f"Ваше количество просроченных заявок - {expired_consultations.expired_consultations}\n"
        f"Верим и ждем\n\n"
        f"Посмотреть заявки на сайте:\n {link_neneprasno}\n"
        f"----\n"
        f"В работе количество  заявок - {expiring_consultations.active_consultations}\n"
        f"Истекает срок у количество заявок - {expiring_consultations.expiring_consultations}\n"
        f"\n[Открыть Trello](https://trello.com/{TRELLO_BORD_ID}/?filter=member:"
        f"{username_trello}/?filter=overdue:true)\n\n"
    )
    await reply_message(update=update, text=message)


menu_conversation = ConversationHandler(
    allow_reentry=True,
    persistent=True,
    name="menu_conversation",
    entry_points=[CommandHandler("menu", menu)],
    states={
        states.MENU_STATE: [
            CallbackQueryHandler(
                button_statistic_month_callback, pattern=callback_data.CALLBACK_STATISTIC_MONTH_COMMAND
            ),
            CallbackQueryHandler(button_reaction_callback, pattern=callback_data.CALLBACK_STATISTIC_WEEK_COMMAND),
            CallbackQueryHandler(
                button_overdue_requests_callback, pattern=callback_data.CALLBACK_OVERDUE_REQUESTS_COMMAND
            ),
            CallbackQueryHandler(
                button_actual_requests_callback, pattern=callback_data.CALLBACK_ACTUAL_REQUESTS_COMMAND
            ),
            CallbackQueryHandler(configurate_timezone, pattern=callback_data.CALLBACK_CONFIGURATE_TIMEZONE_COMMAND),
        ],
        **states_timezone_conversation_dict,
    },
    fallbacks=[],
)
