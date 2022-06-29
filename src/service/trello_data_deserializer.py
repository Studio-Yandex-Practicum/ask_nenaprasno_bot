from dataclasses import dataclass


@dataclass
class TrelloData:
    url: str


async def trello_deserializer(trello_response_json):
    url = trello_response_json["model"]["url"]
    return TrelloData(url)
