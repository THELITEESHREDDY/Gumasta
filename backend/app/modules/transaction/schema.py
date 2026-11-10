from datetime import date, time

from pydantic import BaseModel, ConfigDict, Field

from .models import PartyType


class TransactionCreate(BaseModel):
    order_id: str

    amount: float = Field(gt=0)

    date: date
    time: time

    sender_type: PartyType
    sender_id: str
    sender_mobile_number: str = Field(pattern=r"^\d{10}$")

    receiver_type: PartyType
    receiver_id: str
    receiver_mobile_number: str = Field(pattern=r"^\d{10}$")


class TransactionResponse(BaseModel):
    id: str
    order_id: str

    amount: float
    date: date
    time: time

    sender_type: PartyType
    sender_id: str
    sender_mobile_number: str

    receiver_type: PartyType
    receiver_id: str
    receiver_mobile_number: str

    model_config = ConfigDict(from_attributes=True)