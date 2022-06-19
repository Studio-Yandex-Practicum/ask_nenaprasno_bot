from core import config
from api_client_functions import (
    SiteService, APICallService,
    APICallServiceDUMB
)

API_SERVICE_DUBM = APICallServiceDUMB(config.SITE_URL)
API_SERVICE = APICallService(config.SITE_URL)
SITE_SERVICE = SiteService(API_SERVICE_DUBM)

CLIENT_METHODS = {
    'tgbot/stat': SITE_SERVICE.get_stat,
    'tgbot/bill': SITE_SERVICE.get_stat,
    'tgbot/auth': SITE_SERVICE.authenticate_user,
    'tgbot/user': SITE_SERVICE.set_user_timezone
}


async def main(url, **kwargs):
    endpoint = url.replace(config.SITE_URL, '')
    service_called = '/'.join(endpoint.split('/')[0:2])
    if service_called in CLIENT_METHODS:
        function = CLIENT_METHODS[service_called]
        if function.__name__ == 'get_stat':
            data = await function(endpoint)
        elif function.__name__ == 'authenticate_user':
            telegram_id = kwargs['telegram_id']
            data = await function(endpoint, telegram_id)
        else:
            telegram_id = kwargs['telegram_id']
            user_timizone = kwargs['user_timezone']
            data = await function(endpoint, telegram_id, user_timizone)
        return data
