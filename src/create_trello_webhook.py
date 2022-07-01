import asyncio
import json

import httpx

from core import config
from core.logger import logging

client = httpx.AsyncClient()


async def create_trello_webhook():
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
    request = client.build_request(method="POST", url=config.TRELLO_URL, headers=headers, params=params)
    response = await client.send(request, stream=True)
    data = (await response.aread()).decode("utf-8")
    try:
        json_data = json.loads(data)
        logging.info(f"Trello webhook id: {json_data['id']}")
    except json.decoder.JSONDecodeError:
        logging.info(data)


async def main():
    await create_trello_webhook()


asyncio.run(main())
