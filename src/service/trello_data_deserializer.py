from dataclasses import dataclass, field

from dataclasses_json import config, dataclass_json


@dataclass_json
@dataclass(frozen=True)
class TrelloBoardModel:
    board_url: str = field(metadata=config(field_name="url"))


@dataclass_json
@dataclass(frozen=True)
class TrelloCardModel:
    card_url: str = field(metadata=config(field_name="shortLink"))


@dataclass_json
@dataclass(frozen=True)
class TrelloBoardActionDataModel:
    user_id: str = field(metadata=config(field_name="idMember"))
    card: TrelloCardModel


@dataclass_json
@dataclass(frozen=True)
class TrelloBoardActionModel:
    data: TrelloBoardActionDataModel = field(metadata=config(field_name="data"))


@dataclass_json
@dataclass(frozen=True)
class TrelloDeserializerModel:
    board_model: TrelloBoardModel = field(metadata=config(field_name="model"))
    board_action: TrelloBoardActionModel = field(metadata=config(field_name="action"))
