import logging
from string import Template
from typing import List, Optional, Union

from telegram import Bot, ReplyKeyboardMarkup, Update
from telegram.constants import ParseMode
from telegram.error import TelegramError
from telegram.ext import CallbackContext

from decorators.limits import cheat_limits_of_telegram
from service.api_client.models import MonthStat, WeekStat


@cheat_limits_of_telegram
async def send_message(
    bot: Bot,
    chat_id: int,
    text: str,
    reply_markup: Optional[ReplyKeyboardMarkup] = None,
) -> bool:
    """
    Send simple text message.
    :param bot: Bot
    :param chat_id: int
    :param text: str
    :param reply_markup: ReplyKeyboardMarkup | None
    """
    try:
        await bot.send_message(
            chat_id=chat_id,
            text=text,
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=reply_markup,
        )
        return True
    except TelegramError:
        logging.exception("The error sending the message to the chat: %d", chat_id)
        return False


@cheat_limits_of_telegram
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
            text=new_text,
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=reply_markup,
        )
        return True
    except TelegramError:
        logging.exception("The error editing the message to the chat: %d", update.effective_chat.id)
        return False


@cheat_limits_of_telegram
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
        await message.reply_markdown(text=text, reply_markup=reply_markup)
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
        await send_message(bot=context.bot, chat_id=user_statistic.telegram_id, text=message, reply_markup=reply_markup)
