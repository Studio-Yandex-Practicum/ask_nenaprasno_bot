from dataclasses import dataclass, field

from dataclasses_json import config, dataclass_json


@dataclass_json
@dataclass(frozen=True)
class CloseDeserializerModel:
    consultation_id: str = field(metadata=config(field_name="consultation_id"))


@dataclass_json
@dataclass(frozen=True)
class MessageFeedbackDeserializerModel:
    consultation_id: str = field(metadata=config(field_name="consultation_id"))
    consultation_url: str = field(metadata=config(field_name="consultation_url"))
    trello_card_id: str = field(metadata=config(field_name="trello_card_id"))
    username_trello: str = field(metadata=config(field_name="username_trello"))
    telegram_id: str = field(metadata=config(field_name="telegram_id"))


@dataclass_json
@dataclass(frozen=True)
class AssignDeserializerModel:
    consultation_id: str = field(metadata=config(field_name="consultation_id"))
    consultation_url: str = field(metadata=config(field_name="consultation_url"))
    due: str = field(metadata=config(field_name="due"))
    trello_card_id: str = field(metadata=config(field_name="trello_card_id"))
    username_trello: str = field(metadata=config(field_name="username_trello"))
    telegram_id: str = field(metadata=config(field_name="telegram_id"))
