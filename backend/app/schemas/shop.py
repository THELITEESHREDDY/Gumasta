from uuid import UUID
from datetime import datetime

from pydantic import BaseModel, Field, ConfigDict


class ShopBase(BaseModel):
    name: str = Field(min_length=1, max_length=150)
    gst_id: str | None = Field(default=None, max_length=15)
    address: str = Field(min_length=1, max_length=500)
    contact: str = Field(pattern=r"^\+?[0-9]{10,15}$")


class ShopCreate(ShopBase):
    pass


class ShopUpdate(BaseModel):
    name: str | None = Field(
        default=None, min_length=1, max_length=150
    )
    gst_id: str | None = Field(
        default=None, max_length=15
    )
    address: str | None = Field(
        default=None, min_length=1, max_length=500
    )
    contact: str | None = Field(
        default=None, pattern=r"^\+?[0-9]{10,15}$"
    )


class ShopResponse(ShopBase):
    id: UUID
    owner_id: UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)