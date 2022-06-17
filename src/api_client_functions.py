import requests
import json

from core import config
from api_client_dumpdata import (
    TGBOT_AUTH, TGBOT_STAT_MONTHLY,
)


def get_stat(endpoint):
    url = config.WEBHOOK_URL + endpoint
    # response = requests.get(url)
    response = json.dumps(TGBOT_STAT_MONTHLY)
    response = json.loads(response)
    return response


def authenticate_user(endpoint, telegram_id):
    url = config.WEBHOOK_URL + endpoint
    # response = requests.post(url, data={'telegram_id': telegram_id})
    response = json.dumps(TGBOT_AUTH)
    response = json.loads(response)
    return response


def set_user_timezone(endpoint, telegram_id, user_timizone):
    # url = config.WEBHOOK_URL + endpoint
    # response = requests.put(
    #     url,
    #     data= {
    #         'telegram_id': telegram_id,
    #         'user_timizone': user_timizone
    #     }
    # )
    return 'OK'
