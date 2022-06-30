from dataclasses import dataclass


@dataclass
class TrelloData:
    url: str
    doctor_id: str


async def trello_deserializer(trello_response_json):
    url = trello_response_json["model"]["url"]
    doctor_id = trello_response_json["action"]["id"]
    return TrelloData(url, doctor_id)
