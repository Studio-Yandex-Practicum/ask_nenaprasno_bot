from pydantic import BaseModel


class ClosedConsultationContext(BaseModel):
    consultation_id: str

    class Config:  # pylint: disable=R0903
        allow_mutation = False
