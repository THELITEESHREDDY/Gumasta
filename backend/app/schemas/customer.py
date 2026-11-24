from uuid import UUID
from datetime import datetime

from pydantic import BaseModel, Field, ConfigDict


class CustomerBase(BaseModel):
    name: str = Field(
        min_length=1, max_length=100
    )

    mobile: str = Field(
        pattern=r"^\+?[0-9]{10,15}$"
    )

    alternate_mobile: str | None = Field(
        default=None,
        pattern=r"^\+?[0-9]{10,15}$"
    )

    address: str | None = Field(
        default=None,
        max_length=500
    )


class CustomerCreate(CustomerBase):
    pass


class CustomerUpdate(BaseModel):
    name: str | None = Field(
        default=None,
        min_length=1,
        max_length=100
    )

    mobile: str | None = Field(
        default=None,
        pattern=r"^\+?[0-9]{10,15}$"
    )

    alternate_mobile: str | None = Field(
        default=None,
        pattern=r"^\+?[0-9]{10,15}$"
    )

    address: str | None = Field(
        default=None,
        max_length=500
    )


class CustomerResponse(CustomerBase):
    id: UUID
    shop_id: UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)