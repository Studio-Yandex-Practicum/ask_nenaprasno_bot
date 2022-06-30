from http import HTTPStatus
from typing import Optional

from service.api_client.base import AbstractAPIService
from service.api_client.models import BillStat, MonthStat, UserData, UserMonthStat, UserWeekStat, WeekStat


class MockAPIService(AbstractAPIService):
    async def get_bill(self) -> BillStat:
        return BillStat(telegram_ids=[12345685, 78945656, 4564512312])

    async def get_week_stat(self) -> list[WeekStat]:
        return [
            WeekStat(
                telegram_id=971746479,
                user_time_zone="UTC+3",
                user_name_in_trello="user1@trello",
                last_week_user_tickets_closed=10,
                last_week_user_tickets_not_expiring=2,
                last_week_user_tickets_expiring=1,
                last_week_user_tickets_expired=1,
                last_week_user_tickets_in_work=4,
                last_week_user_tickets_all=14,
            ),
            WeekStat(
                telegram_id=721889325,
                user_time_zone="UTC+3",
                user_name_in_trello="user2@trello",
                last_week_user_tickets_closed=5,
                last_week_user_tickets_not_expiring=3,
                last_week_user_tickets_expiring=2,
                last_week_user_tickets_expired=1,
                last_week_user_tickets_in_work=6,
                last_week_user_tickets_all=16,
            ),
        ]

    async def get_month_stat(self) -> list[MonthStat]:
        return [
            MonthStat(
                telegram_id=971746479,
                user_time_zone="UTC+3",
                user_tickets_closed=10,
                user_rating=3.2,
                user_ticket_resolve_avg_time=4.1,
            ),
            MonthStat(
                telegram_id=721889325,
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
            last_week_user_tickets_not_expiring=2,
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

    async def authenticate_user(self, telegram_id: int) -> Optional[None]:
        return UserData(
            user_name="Bob",
            user_time_zone="UTC+3",
            user_name_in_trello="user1@telegram",
        )

    async def set_user_timezone(self, telegram_id: int, user_time_zone: str) -> HTTPStatus:
        return HTTPStatus.OK
