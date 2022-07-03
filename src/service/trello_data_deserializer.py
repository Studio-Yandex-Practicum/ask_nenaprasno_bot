from dataclasses import dataclass, field

from dataclasses_json import config, dataclass_json


@dataclass_json
@dataclass(frozen=True)
class TrelloModel:
    case_url: str = field(metadata=config(field_name="url"))


@dataclass_json
@dataclass(frozen=True)
class TrelloAction:
    doctor_id: str = field(metadata=config(field_name="id"))


@dataclass_json
@dataclass(frozen=True)
class TrelloData:
    model: TrelloModel
    action: TrelloAction
