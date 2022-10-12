from datetime import timedelta
from typing import Dict, List

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import CallbackQueryHandler, CommandHandler, ContextTypes, ConversationHandler

from constants import callback_data, states
from conversation.timezone import set_timezone_from_keyboard, timezone_conversation
from core.config import URL_SERVICE_RULES
from core.send_message import reply_message
from core.utils import build_consultation_url, build_trello_url, get_word_case
from decorators.logger import async_error_logger
from get_timezone import get_user_timezone
from service.api_client import APIService

OVERDUE_TEMPLATE = (
    "Время и стекло 😎\n"
    "Ваше количество просроченных заявок - {expired_consultations}\n"
    "Верим и ждем.\n\n"
    "{link_nenaprasno}\n"
    "----\n"
    "В работе количество заявок - {active_consultations}\n"
    "[Открыть Trello]({trello_url})\n\n"
)

ACTUAL_TEMPLATE = (
    "У вас в работе {active_consultations} {declination_consultation}.\n"
    "{link_nenaprasno}\n"
    "[Открыть Trello]({trello_url})\n\n"
)


@async_error_logger(name="conversation.menu_commands.menu")
async def menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    """
    Displays the menu.
    """
    user_tz = await get_user_timezone(int(update.effective_user.id), context)
    menu_buttons = [
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
        [
            InlineKeyboardButton(
                text=f"Настроить часовой пояс (сейчас {user_tz})",
                callback_data=callback_data.CALLBACK_CONFIGURATE_TIMEZONE_COMMAND,
            )
        ],
    ]
    await reply_message(update=update, text="Меню", reply_markup=InlineKeyboardMarkup(menu_buttons))
    return states.MENU_STATE


@async_error_logger(name="conversation.requests.actual_requests_callback")
async def button_reaction_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    """
    Sends a list of current requests/requests to the user.
    """
    await reply_message(update=update, text="button reaction callback")
    return states.MENU_STATE


def format_average_user_answer_time(time: float | None) -> str:
    if time is None:
        return ""

    average_answer_time = timedelta(days=0, hours=0, milliseconds=time)
    days = average_answer_time.days
    hours = average_answer_time.seconds // 3600
    output_days = get_word_case(days, "день", "дня", "дней")
    output_hours = get_word_case(hours, "час", "часа", "часов")

    return f"***Среднее время ответа*** - {days} {output_days} {hours} {output_hours}\n"


def format_rating(rating: float | None) -> str:
    if rating is None:
        return ""

    return f"***Рейтинг*** - {rating:.1f}\n"


@async_error_logger(name="conversation.requests.button_statistic_month_callback")
async def button_statistic_month_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Send monthly statistics at the user's request.
    """
    service = APIService()
    telegram_id = update.effective_user.id
    user_statistics = await service.get_user_month_stat(telegram_id=telegram_id)

    if user_statistics is None:
        await update.callback_query.message.reply_text(text="Данные недоступны!")
        return

    if user_statistics.closed_consultations > 0:
        message = (
            'С начала месяца вы сделали очень много для "Просто спросить" 🔥\n'
            f"***Количество закрытых заявок*** - {user_statistics.closed_consultations}\n"
            f"{format_rating(user_statistics.rating)}"
            f"{format_average_user_answer_time(user_statistics.average_user_answer_time)}"
            "\nМы рады работать в одной команде :)\n"
            "Так держать!"
        )
    else:
        message = "К сожалению у вас не было отвеченных заявок :(\nМы верим, что в следующем месяце все изменится! :)"

    await reply_message(update=update, text=message)


def make_consultations_list(consultations_list: List[Dict]) -> str:
    if any(consultations_list):
        return (
            "Посмотреть заявки на сайте:\n"
            + "\n".join(
                [
                    f"{number}. [Заявка {consultation['number']}]({build_consultation_url(consultation['id'])})"
                    for number, consultation in enumerate(consultations_list, start=1)
                ]
            )
            + "\n"
        )
    return ""


@async_error_logger(name="conversation.requests.button_actual_requests_callback")
async def button_actual_requests_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Sends a list of active consultations to the user.
    """
    service = APIService()
    telegram_id = update.effective_user.id
    active_consultations = await service.get_user_active_consultations(telegram_id=telegram_id)

    if active_consultations is None:
        await update.callback_query.message.reply_text(text="Данные недоступны!")
        return

    active_consultations_list = active_consultations.active_consultations_data
    link_nenaprasno = make_consultations_list(active_consultations_list)
    declination_consultation = get_word_case(active_consultations.active_consultations, "заявка", "заявки", "заявок")

    trello_url = build_trello_url(active_consultations.username_trello, overdue=True)

    message = ACTUAL_TEMPLATE.format(
        active_consultations=active_consultations.active_consultations,
        declination_consultation=declination_consultation,
        link_nenaprasno=link_nenaprasno,
        trello_url=trello_url,
    )
    await reply_message(update=update, text=message)


@async_error_logger(name="conversation.requests.button_overdue_requests_callback")
async def button_overdue_requests_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Send information about expiring and overdue consultation.
    """
    service = APIService()
    telegram_id = update.effective_user.id
    expired_consultations = await service.get_user_expired_consultations(telegram_id=telegram_id)
    active_consultations = await service.get_user_active_consultations(telegram_id=telegram_id)

    if expired_consultations is None or active_consultations is None:
        await update.callback_query.message.reply_text(text="Данные недоступны")
        return

    expired_consultations_list = expired_consultations.expired_consultations_data
    link_nenaprasno = make_consultations_list(expired_consultations_list)
    trello_url = build_trello_url(expired_consultations.username_trello, overdue=True)

    message = OVERDUE_TEMPLATE.format(
        expired_consultations=expired_consultations.expired_consultations,
        link_nenaprasno=link_nenaprasno,
        active_consultations=active_consultations.active_consultations,
        trello_url=trello_url,
    )
    await reply_message(update=update, text=message)


menu_conversation = ConversationHandler(
    allow_reentry=True,
    persistent=True,
    name="menu_conversation",
    entry_points=[CommandHandler("menu", menu), timezone_conversation],
    states={
        states.MENU_STATE: [
            CallbackQueryHandler(
                button_statistic_month_callback, pattern=callback_data.CALLBACK_STATISTIC_MONTH_COMMAND
            ),
            CallbackQueryHandler(
                button_overdue_requests_callback, pattern=callback_data.CALLBACK_OVERDUE_REQUESTS_COMMAND
            ),
            CallbackQueryHandler(
                button_actual_requests_callback, pattern=callback_data.CALLBACK_ACTUAL_REQUESTS_COMMAND
            ),
            CallbackQueryHandler(
                set_timezone_from_keyboard, pattern=callback_data.CALLBACK_CONFIGURATE_TIMEZONE_COMMAND
            ),
            timezone_conversation,
        ],
    },
    fallbacks=[],
)
