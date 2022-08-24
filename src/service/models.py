from dataclasses import dataclass, field

from dataclasses_json import config, dataclass_json


@dataclass_json
@dataclass
class HealthCheckResponseModel:
    bot_is_avaliable: bool = False
    site_api_is_avaliable: bool = False


@dataclass_json
@dataclass(frozen=True)
class FeedbackConsultationModel:
    consultation_id: str = field(metadata=config(field_name="consultation_id"))
    # ! site API does not provide the consultation number right now. It will be fixed in the future
    # consultation_number: str = field(metadata=config(field_name="consultation_number"))
    consultation_response: str = field(metadata=config(field_name="consultation_response"))
    username_trello: str = field(metadata=config(field_name="username_trello"))
    telegram_id: str = field(metadata=config(field_name="telegram_id"))


@dataclass_json
@dataclass(frozen=True)
class ConsultationModel:
    consultation_id: str = field(metadata=config(field_name="consultation_id"))
    # ! site API does not provide the consultation number right now. It will be fixed in the future
    # consultation_number: str = field(metadata=config(field_name="consultation_number"))
    trello_card_id: str = field(metadata=config(field_name="trello_card_id"))
    username_trello: str = field(metadata=config(field_name="username_trello"))
    telegram_id: str = field(metadata=config(field_name="telegram_id"))


@dataclass_json
@dataclass(frozen=True)
class AssignedConsultationModel(ConsultationModel):
    due: str = field(metadata=config(field_name="due"))


@dataclass_json
@dataclass(frozen=True)
class ClosedConsultationModel:
    consultation_id: str = field(metadata=config(field_name="consultation_id"))
    telegram_id: str = field(metadata=config(field_name="telegram_id"))
