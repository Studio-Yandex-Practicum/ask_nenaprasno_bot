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
from texts import buttons as texts_buttons
from texts import common as texts_common
from texts import conversations as texts_conversations


@async_error_logger(name="conversation.menu_commands.menu")
async def menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    """
    Displays the menu.
    """
    user_tz = await get_user_timezone(int(update.effective_user.id), context)
    menu_buttons = [
        [
            InlineKeyboardButton(
                texts_buttons.BTN_MONTH_STAT, callback_data=callback_data.CALLBACK_STATISTIC_MONTH_COMMAND
            ),
        ],
        [
            InlineKeyboardButton(
                texts_buttons.BTN_IN_PROGRESS, callback_data=callback_data.CALLBACK_ACTUAL_REQUESTS_COMMAND
            )
        ],
        [
            InlineKeyboardButton(
                texts_buttons.BTN_OVERDUE, callback_data=callback_data.CALLBACK_OVERDUE_REQUESTS_COMMAND
            )
        ],
        [
            InlineKeyboardButton(
                texts_buttons.BTN_RULES,
                url=URL_SERVICE_RULES,
            )
        ],
        [
            InlineKeyboardButton(
                texts_buttons.BTN_TIMEZONE.format(user_tz=user_tz),
                callback_data=callback_data.CALLBACK_CONFIGURATE_TIMEZONE_COMMAND,
            )
        ],
    ]
    await reply_message(update, texts_buttons.BTN_MENU, reply_markup=InlineKeyboardMarkup(menu_buttons))
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
    output_days = get_word_case(days, *texts_common.PLURAL_DAY)
    output_hours = get_word_case(hours, *texts_common.PLURAL_HOUR)

    return texts_conversations.AVERAGE_ANSWER_TIME.format(
        days=days, output_days=output_days, hours=hours, output_hours=output_hours
    )


def format_rating(rating: float | None) -> str:
    if rating is None:
        return ""

    return texts_conversations.RATING.format(rating=rating)


@async_error_logger(name="conversation.requests.button_statistic_month_callback")
async def button_statistic_month_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Send monthly statistics at the user's request.
    """
    service = APIService()
    telegram_id = update.effective_user.id
    user_statistics = await service.get_user_month_stat(telegram_id=telegram_id)

    if user_statistics is None:
        await update.callback_query.message.reply_text(text=texts_common.DATA_NOT_AVAILABLE)
        return

    if user_statistics.closed_consultations > 0:
        message = texts_conversations.MONTH_STAT_GOOD.format(
            closed_consultations=user_statistics.closed_consultations,
            rating=format_rating(user_statistics.rating),
            average_answer_time=format_average_user_answer_time(user_statistics.average_user_answer_time),
        )
    else:
        message = texts_conversations.MONTH_STAT_BAD

    await reply_message(update=update, text=message)


def make_consultations_list(consultations_list: List[Dict]) -> str:
    if any(consultations_list):
        return (
            texts_conversations.CONSULTATION_LIST_HEAD
            + "\n"
            + "\n".join(
                [
                    texts_conversations.CONSULTATION_LIST_ITEM.format(
                        number=number,
                        consultation_number=consultation["number"],
                        consultations_url=build_consultation_url(consultation["id"]),
                    )
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
        await update.callback_query.message.reply_text(text=texts_common.DATA_NOT_AVAILABLE)
        return

    active_consultations_list = active_consultations.active_consultations_data
    link_nenaprasno = make_consultations_list(active_consultations_list)
    declination_consultation = get_word_case(
        active_consultations.active_consultations, *texts_common.PLURAL_CONSULTATION
    )

    trello_url = build_trello_url(active_consultations.username_trello, overdue=True)

    message = texts_conversations.ACTUAL_TEMPLATE.format(
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
        await update.callback_query.message.reply_text(text=texts_common.DATA_NOT_AVAILABLE)
        return

    expired_consultations_list = expired_consultations.expired_consultations_data
    link_nenaprasno = make_consultations_list(expired_consultations_list)
    trello_url = build_trello_url(expired_consultations.username_trello, overdue=True)

    message = texts_conversations.OVERDUE_TEMPLATE.format(
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
