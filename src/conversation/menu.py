from datetime import timedelta
from typing import Dict, List

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import CallbackQueryHandler, CommandHandler, ContextTypes, ConversationHandler

from constants import callback_data, states
from conversation.timezone import set_timezone_from_keyboard, timezone_conversation
from core.config import TRELLO_BORD_ID, URL_ASK_NENAPRASNO, URL_SERVICE_RULES
from core.send_message import reply_message
from decorators.logger import async_error_logger
from service.api_client import APIService


@async_error_logger(name="conversation.menu_commands.menu")
async def menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    """
    Displays the menu.
    """
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
                text="Настроить часовой пояс", callback_data=callback_data.CALLBACK_CONFIGURATE_TIMEZONE_COMMAND
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

    return f"***Среднее время ответа*** - {days} дней {hours} часа\n"


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
        message = "К сожалению у вас не было отвеченных завок :(\nМы верим, что в следующем месяце все изменится! :)"

    await reply_message(update=update, text=message)


def make_consultations_list(consultations_list: List[Dict]) -> str:
    url_base = f"{URL_ASK_NENAPRASNO}/doctor/consultation/"

    return (
        "\n".join(
            [
                f"{number}. [Заявка №{consultation['number']}]({url_base}{consultation['id']})"
                for number, consultation in enumerate(consultations_list, start=1)
            ]
        )
        + "\n"
    )


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

    username_trello = active_consultations.username_trello
    active_consultations_list = active_consultations.active_consultations_data
    link_neneprasno = make_consultations_list(active_consultations_list)

    message = (
        f"У вас в работе {active_consultations.active_consultations} заявок.\n"
        f"Посмотреть заявки на сайте:\n{link_neneprasno}\n"
        f"[Открыть Trello](https://trello.com/{TRELLO_BORD_ID}/?filter=member:"
        f"{username_trello}/?filter=overdue:true)\n\n"
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

    username_trello = expired_consultations.username_trello
    expired_consultations_list = expired_consultations.expired_consultations_data
    link_neneprasno = make_consultations_list(expired_consultations_list)

    message = (
        f"Время и стекло 😎\n"
        f"Ваше количество просроченных заявок - {expired_consultations.expired_consultations}\n"
        f"Верим и ждем.\n\n"
        f"Посмотреть заявки на сайте:\n{link_neneprasno}\n"
        f"----\n"
        f"В работе количество заявок - {active_consultations.active_consultations}\n"
        f"Открыть [Trello](https://trello.com/{TRELLO_BORD_ID}/?filter=member:"
        f"{username_trello}/?filter=overdue:true)\n\n"
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
