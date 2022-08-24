import asyncio
from datetime import datetime, timedelta

from core.logger import logger

All_DURATION = timedelta(milliseconds=40)
USER_DURATIN = timedelta(seconds=1)
WITHOUT_CHECK = False


def cheat_limits_of_telegram(func):
    async def wrapper(*args, **kwargs):
        if WITHOUT_CHECK:
            return await func(*args, **kwargs)
        chat_id = kwargs.get("chat_id", kwargs.get("update"))
        try:
            if not isinstance(chat_id, int):
                chat_id = chat_id.effective_chat.id
            delay = new_limits.delay(telegram_id=chat_id)
            await asyncio.sleep(delay=delay)
        except AttributeError as error:
            logger.error("Error when calling the function: %s, error: %s", func.__name__, error)
        return await func(*args, **kwargs)

    return wrapper


class Limits:
    def __init__(self):
        self.users_last_sending = {}
        self.time_last_sending = datetime.now()

    def delay(self, telegram_id: int) -> float:
        currently = datetime.now()
        point_for_all = self.time_last_sending + All_DURATION
        point_for_user = self.users_last_sending.get(telegram_id, currently - 3 * USER_DURATIN) + USER_DURATIN

        if currently < point_for_all and currently < point_for_user:
            time_sending = max(point_for_all, point_for_user)
        elif point_for_all <= currently < point_for_user:
            time_sending = point_for_user
        elif point_for_user <= currently < point_for_all:
            time_sending = point_for_all
        else:
            time_sending = currently

        self.time_last_sending = time_sending
        self.users_last_sending[telegram_id] = time_sending
        return (time_sending - currently).total_seconds()

    def force(self, telegram_id: int):
        currently = datetime.now()
        self.time_last_sending = currently
        self.users_last_sending[telegram_id] = currently

    def refresh(self):
        currently = datetime.now()
        self.time_last_sending = currently
        self.users_last_sending = {}


new_limits = Limits()
