import json

import httpx

from core import config
from core.logger import logger


def create_trello_webhook():
    """
    Function that create request Trello Api to create or check webhook

    result: if webhook is created -> webhook_id
            if webhook exists -> A webhook with that callback, model, and token already exists
    """
    headers = {"Accept": "application/json"}
    params = {
        "callbackURL": f"{config.WEBHOOK_URL}/trelloWebhookApi",
        "idModel": config.TRELLO_ID_MODEL,
        "key": config.TRELLO_API_KEY,
        "token": config.TRELLO_TOKEN,
    }
    with httpx.Client() as client:
        request = client.build_request(
            method="POST", url="https://api.trello.com/1/webhooks/", headers=headers, params=params
        )
        response = client.send(request)
    try:
        response = response.json()
        webhook_id = response.get("id")
        if webhook_id:
            logger.info("Trello webhook id: %s", webhook_id)
        else:
            logger.info("Something got wrong: %s", response.get("message"))
    except json.decoder.JSONDecodeError:
        logger.info(response.text)
