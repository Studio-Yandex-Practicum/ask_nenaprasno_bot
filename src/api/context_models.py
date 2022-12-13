from pydantic import BaseModel


class HealthCheckResponseContext(BaseModel):
    bot_is_avaliable: bool = False
    site_api_is_avaliable: bool = False


class ClosedConsultationContext(BaseModel):
    consultation_id: str

    class Config:  # pylint: disable=R0903
        allow_mutation = False


class ConsultationContext(BaseModel):
    consultation_id: str
    consultation_number: int
    username_trello: str
    telegram_id: int
    trello_card_id: str

    class Config:  # pylint: disable=R0903
        allow_mutation = False


class FeedbackConsultationContext(ConsultationContext):
    feedback: str

    class Config:  # pylint: disable=R0903
        allow_mutation = False


class AssignedConsultationContext(ConsultationContext):
    due: str

    class Config:  # pylint: disable=R0903
        allow_mutation = False
