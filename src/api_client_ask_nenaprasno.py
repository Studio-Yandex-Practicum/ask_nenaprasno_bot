import re
from core import config
from api_client_functions import (
    get_stat, authenticate_user,
    set_user_timezone
)

CLIENT_METHODS = {
    'tgbot/stat': get_stat,
    'tgbot/bill': get_stat,
    'tgbot/auth': authenticate_user,
    'tgbot/user': set_user_timezone
}


def main(url, **kwargs):
    endpoint = url.replace(config.WEBHOOK_URL, '')
    for i in CLIENT_METHODS:
        search_result = re.search(i, endpoint)
        if search_result is not None:
            function = CLIENT_METHODS[search_result.group()]
            if not kwargs:
                data = function(endpoint)
                return data
            else:
                try:
                    telegram_id = kwargs['telegram_id']
                except:
                    raise Exception(
                        'Unvalid Argument!'
                    )
                if len(kwargs.keys()) == 1:
                    data = function(endpoint, telegram_id)
                    return data
                else:
                    try:
                        user_timizone = kwargs['user_timizone']
                    except:
                        raise Exception(
                            'Unvalid Argument!'
                        )
                    data = function(endpoint, telegram_id, user_timizone)
                    return data
