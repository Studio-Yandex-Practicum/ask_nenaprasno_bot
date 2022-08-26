import asyncio
from datetime import datetime, timedelta

from core.logger import logger

MODE_ACCOUNTING_LIMIT_TELEGRAM = True
AMOUNT_MESSAGES_PER_SECOND = 30


def regulating_time_sending_messages(func):
    async def wrapper(*args, **kwargs):
        if not MODE_ACCOUNTING_LIMIT_TELEGRAM:
            return await func(*args, **kwargs)
        try:
            chat_id = kwargs.get("chat_id") if "chat_id" in kwargs else kwargs.get("update").effective_chat.id
            delay = new_limits.delay(telegram_id=chat_id)
            await asyncio.sleep(delay=delay)
        except AttributeError as error:
            logger.error("Error when calling the function: %s, error: %s", func.__name__, error)
        return await func(*args, **kwargs)

    return wrapper


class Limits:  # pylint: disable=too-few-public-methods
    def __init__(self):
        self.curent_second: datetime = datetime.now()
        self.curent_second = self.curent_second - timedelta(microseconds=self.curent_second.microsecond)
        # a list of messages sent and ready to go in the future
        # format dict = {telegram_id: date of send}
        # first dict is previous second, next dict - current second and ...
        self.sending_list_broken_down_by_seconds: list(dict(int, datetime)) = [
            {},
        ]

    def delay(self, telegram_id: int) -> float:
        currently = datetime.now()

        # we remove the unnecessary first elements of list - before previous second at the moment
        new_current_second = currently - timedelta(microseconds=currently.microsecond)
        diff = int((new_current_second - self.curent_second).total_seconds())
        if diff >= len(self.sending_list_broken_down_by_seconds):
            self.sending_list_broken_down_by_seconds = [
                {},
            ]
        else:
            self.sending_list_broken_down_by_seconds = self.sending_list_broken_down_by_seconds[diff:]
        self.curent_second = new_current_second

        # determination of the first possible time of sending a message
        # based on the sending data from the previous second
        time_sending_message_to_prev_second = self.sending_list_broken_down_by_seconds[0].get(telegram_id)
        if time_sending_message_to_prev_second is None:
            planned_time_sending_message = currently
        else:
            if time_sending_message_to_prev_second + timedelta(seconds=1) > currently:
                planned_time_sending_message = time_sending_message_to_prev_second + timedelta(seconds=1)
            else:
                planned_time_sending_message = currently

        # we go through the list starting from the current second
        # and to search at what second you can send a message
        for i, sending_list in enumerate(self.sending_list_broken_down_by_seconds[1:]):
            if sending_list.get(telegram_id) is None and len(sending_list) < AMOUNT_MESSAGES_PER_SECOND:
                sending_list[telegram_id] = planned_time_sending_message
                return (planned_time_sending_message - currently).total_seconds()
            # determine the new planned time of sending the message
            if sending_list.get(telegram_id) is None:
                planned_time_sending_message = self.curent_second + timedelta(seconds=i + 1)
            else:
                planned_time_sending_message = sending_list.get(telegram_id) + timedelta(seconds=1)

        # we don't seek place in existence dicts -> add new dict for new second
        self.sending_list_broken_down_by_seconds.append({telegram_id: planned_time_sending_message})
        return (planned_time_sending_message - currently).total_seconds()


new_limits = Limits()
