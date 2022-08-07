import logging
from string import Template
from typing import List, Optional, Union

from telegram import Bot, ReplyKeyboardMarkup, Update
from telegram.constants import ParseMode
from telegram.error import TelegramError
from telegram.ext import CallbackContext

from core.config import TRELLO_BORD_ID
from service.api_client.models import MonthStat, WeekStat
from service.models import ConsultationModel


def text_to_markdown(text: str) -> str:
    """
    Escaping some service characters of MarkdownV2
    """
    return text.replace(".", r"\.").replace("-", r"\-").replace("+", r"\+").replace("!", r"\!")


async def send_message(
    context: CallbackContext,
    chat_id: int,
    text: str,
    reply_markup: Optional[ReplyKeyboardMarkup] = None,
) -> bool:
    """
    Send simple text message.
    :param context: CallbackContext
    :param chat_id: int
    :param text: str
    :param reply_markup: ReplyKeyboardMarkup | None
    """
    try:
        await context.bot.send_message(
            chat_id=chat_id,
            text=text_to_markdown(text),
            parse_mode=ParseMode.MARKDOWN_V2,
            reply_markup=reply_markup,
        )
        return True
    except TelegramError:
        logging.exception("The error sending the message to the chat: %d", chat_id)
        return False


async def edit_message(
    update: Update,
    new_text: str,
    reply_markup: Optional[ReplyKeyboardMarkup] = None,
) -> bool:
    """
    Edit text message.
    :param update: Update
    :param new_text: str
    :param reply_markup: ReplyKeyboardMarkup | None
    """
    try:
        await update.callback_query.edit_message_text(
            text=text_to_markdown(new_text),
            parse_mode=ParseMode.MARKDOWN_V2,
            reply_markup=reply_markup,
        )
        return True
    except TelegramError:
        logging.exception("The error editing the message to the chat: %d", update.effective_chat.id)
        return False


async def reply_message(
    update: Update,
    text: str,
    reply_markup: Optional[ReplyKeyboardMarkup] = None,
) -> bool:
    """
    Reply on the message.
    :param update: Update
    :param text: str
    :param reply_markup: ReplyKeyboardMarkup | None
    """
    try:
        message = update.callback_query.message if update.message is None else update.message
        await message.reply_markdown_v2(text=text_to_markdown(text), reply_markup=reply_markup)
        return True
    except TelegramError:
        logging.exception("The error reply on the message to the chat: %d", update.effective_chat.id)
        return False


async def send_statistics(
    context: CallbackContext,
    template_message: Template,
    template_attribute_aliases: dict,
    statistic: List[Union[MonthStat, WeekStat]],
    reply_markup: Optional[ReplyKeyboardMarkup] = None,
):
    """
    Start mailing message with statistics.
    :param context: CallbackContext
    :param template_message: Template
    :param template_attribute_aliases: dict in this dictionary,
        the keys are the names of attributes in the message
        template and the keys are the names of attributes in
        the data object.
    :param statistic: List[Union[UserMonthStat, UserWeekStat]]
    :param reply_markup: ReplyKeyboardMarkup | None
    """
    for user_statistic in statistic:
        message = template_message.substitute(
            {key: getattr(user_statistic, attribute) for key, attribute in template_attribute_aliases.items()}
        )
        await send_message(context=context, chat_id=user_statistic.telegram_id, text=message, reply_markup=reply_markup)


async def send_new_message_notification(bot: Bot, request_data: ConsultationModel) -> None:
    """Sends message about new comment in consultation at site"""
    chat_id = request_data.telegram_id
    text = (
        f"Получено новое сообщение в чате заявки №{request_data.consultation_id}\n"
        f"[Открыть заявку на сайте]({request_data.consultation_url})\n"
        f"[Открыть Trello](https://trello.com/{TRELLO_BORD_ID}/?filter=member:{request_data.username_trello})\n\n"
    )
    try:
        await bot.send_message(
            chat_id=chat_id, parse_mode=ParseMode.MARKDOWN_V2, text=text, disable_web_page_preview=True
        )
    except TelegramError:
        logging.exception("The error sending the message to the chat: %d", chat_id)
