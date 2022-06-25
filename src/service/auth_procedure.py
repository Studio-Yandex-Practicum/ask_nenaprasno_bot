from service import ConreateAPIService


async def auth_telegram_user(telegram_id):
    api_service = ConreateAPIService()
    user_data = await api_service.authenticate_user(telegram_id=telegram_id)
    return user_data
