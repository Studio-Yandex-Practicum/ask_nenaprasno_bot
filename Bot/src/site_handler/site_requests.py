from starlette.applications import Starlette


async def user_is_expert(user_id) -> bool:
    """Является ли юзер экспертом"""
    return True


async def get_current_orders(user_id) -> list:
    """Получить список актуальных заявок"""
    return ['№ 123456', '№ 258647']


async def get_overdue_orders(user_id) -> list:
    """Получить список просроченных заявок"""
    return ['№ 123456', '№ 258647']
