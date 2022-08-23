from datetime import datetime, timedelta

All_DURATION = timedelta(milliseconds=40)
USER_DURATIN = timedelta(seconds=1)
WITHOUT_CHECK = False


class Limits:
    def __init__(self):
        self.users_last_sending = {}
        self.time_last_sending = datetime.now()

    def check(self, telegram_id: int) -> bool:
        if WITHOUT_CHECK:
            return True
        currently = datetime.now()
        if currently < (self.time_last_sending + All_DURATION):
            return False
        if currently < (self.users_last_sending.get(telegram_id, currently - 2 * USER_DURATIN) + USER_DURATIN):
            return False
        self.time_last_sending = currently
        self.users_last_sending[telegram_id] = currently
        return True

    def force(self, telegram_id: int):
        currently = datetime.now()
        self.time_last_sending = currently
        self.users_last_sending[telegram_id] = currently


new_limits = Limits()
