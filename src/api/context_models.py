# disabling too-few-public-methods to avoid error on Config class
# pylint: disable=R0903
from pydantic import BaseModel


class ClosedConsultationContext(BaseModel):
    consultation_id: str

    class Config:
        allow_mutation = False
