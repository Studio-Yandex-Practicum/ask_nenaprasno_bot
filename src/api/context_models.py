from pydantic import BaseModel


class ClosedConsultationContext(BaseModel):
    consultation_id: str

    class Config:  # pylint: disable=R0903
        allow_mutation = False


class ConsultationContext(BaseModel):
    consultation_id: str
    consultation_number: str
    username_trello: str
    telegram_id: str
    trello_card_id: str

    class Config:  # pylint: disable=R0903
        allow_mutation = False
