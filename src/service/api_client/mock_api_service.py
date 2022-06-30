from http import HTTPStatus

from service.api_client.base import AbstractAPIService
from service.api_client.models import BillStat, MonthStat, UserData, UserMonthStat, UserWeekStat, WeekStat


class MockAPIService(AbstractAPIService):
    async def get_bill(self) -> BillStat:
        return BillStat(telegram_name=["user1@telegram", "user2@telegram", "user3@telegram"])

    async def get_week_stat(self) -> list[WeekStat]:
        return [
            WeekStat(
                telegram_name="user1@telegram",
                user_time_zone="UTC+3",
                user_name_in_trello="user1@trello",
                last_week_user_tickets_closed=10,
                last_week_user_tickets_not_expring=2,
                last_week_user_tickets_expiring=1,
                last_week_user_tickets_expired=1,
                last_week_user_tickets_in_work=4,
                last_week_user_tickets_all=14,
            ),
            WeekStat(
                telegram_name="user2@telegram",
                user_time_zone="UTC+3",
                user_name_in_trello="user2@trello",
                last_week_user_tickets_closed=5,
                last_week_user_tickets_not_expring=3,
                last_week_user_tickets_expiring=2,
                last_week_user_tickets_expired=1,
                last_week_user_tickets_in_work=6,
                last_week_user_tickets_all=16,
            ),
        ]

    async def get_month_stat(self) -> list[MonthStat]:
        return [
            MonthStat(
                telegram_name="user1@telegram",
                user_time_zone="UTC+3",
                user_tickets_closed=10,
                user_rating=3.2,
                user_ticket_resolve_avg_time=4.1,
            ),
            MonthStat(
                telegram_name="user2@telegram",
                user_time_zone="UTC+3",
                user_tickets_closed=5,
                user_rating=2.2,
                user_ticket_resolve_avg_time=5.1,
            ),
        ]

    async def get_user_week_stat(self, telegram_name: str) -> UserWeekStat:
        return UserWeekStat(
            user_name_in_trello="user1@telegram",
            last_week_user_tickets_closed=10,
            last_week_user_tickets_not_expring=2,
            last_week_user_tickets_expiring=1,
            last_week_user_tickets_expired=1,
            last_week_user_tickets_in_work=4,
            last_week_user_tickets_all=14,
        )

    async def get_user_month_stat(self, telegram_name: str) -> UserMonthStat:
        return UserMonthStat(
            user_tickets_closed=5,
            user_rating=2.2,
            user_ticket_resolve_avg_time=5.1,
        )

    async def authenticate_user(self, telegram_name: str) -> UserData | None:
        return UserData(
            user_name="Bob",
            user_time_zone="UTC+3",
            user_name_in_trello="user1@telegram",
        )

    async def set_user_timezone(self, telegram_name: str, user_time_zone: str) -> HTTPStatus:
        return HTTPStatus.OK
