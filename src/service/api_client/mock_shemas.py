from http import HTTPStatus

from base import AbstractAPIService
from models import BillStat, MonthStat, MyMonthStat, MyWeekStat, UserData, UserMonthStat, UserWeekStat, WeekStat

GET_BILL_RETURN = ["user1@telegram", "user1@telegram", "user1@telegram"]
WEEK_STAT_RETURN = [
    UserWeekStat("user1@telegram", "UTC+3", "user@trello", "2", "3", "2", "1"),
    UserWeekStat("user1@telegram", "UTC+3", "user2@trello", "2", "3", "2", "1"),
]
MONT_STAT_RETURN = [UserMonthStat("UTC+4", "6", "8", "9.4"), UserMonthStat("UTC+4", "6", "8", "9.4")]
MY_WEEK_STAT_RETURN = MyWeekStat("user2@trello", "3", "2", "1")
MY_MONT_STAT_RETURN = MyMonthStat("6", "8", "9.4")
AUTH_RETURN = UserData("Bob", "UTC+3", "24")


class MockShemasAPIService(AbstractAPIService):
    async def get_bill(self) -> BillStat:
        return BillStat(GET_BILL_RETURN)

    async def get_week_stat(self) -> WeekStat:
        return WeekStat(WEEK_STAT_RETURN)

    async def get_month_stat(self) -> MonthStat:
        return MonthStat(MONT_STAT_RETURN)

    async def get_my_week_stat(self, telegram_id: int) -> MyWeekStat:
        return MY_WEEK_STAT_RETURN

    async def get_my_month_stat(self, telegram_id: int) -> MyMonthStat:
        return MY_MONT_STAT_RETURN

    async def authenticate_user(self, telegram_id: int) -> UserData:
        return AUTH_RETURN

    async def set_user_timezone(self, telegram_id: int, user_timezone: str) -> HTTPStatus:
        return HTTPStatus.OK
