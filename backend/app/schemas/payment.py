from uuid import UUID
from datetime import datetime
from decimal import Decimal
from enum import Enum

from pydantic import BaseModel, Field, ConfigDict

from app.models.payments import PaymentMethod


class PaymentStatus(str, Enum):
    UNPAID = "unpaid"
    PARTIALLY_PAID = "partially_paid"
    PAID = "paid"
    CANCELLED = "cancelled"


class PaymentCreate(BaseModel):
    amount: Decimal = Field(
        gt=0,
        max_digits=14,
        decimal_places=2
    )

    payment_method: PaymentMethod

    reference: str | None = Field(
        default=None,
        max_length=255
    )


class PaymentResponse(BaseModel):
    id: UUID
    order_id: UUID
    amount: Decimal
    payment_method: PaymentMethod
    reference: str | None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class PaymentSummary(BaseModel):
    order_id: UUID
    total_amount: Decimal
    amount_paid: Decimal
    amount_due: Decimal
    payment_status: PaymentStatus