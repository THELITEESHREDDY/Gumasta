from uuid import UUID
from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, Field, ConfigDict, field_validator


class ProductBase(BaseModel):
    name: str = Field(min_length=1, max_length=150)

    cost_price: Decimal = Field(
        ge=0, max_digits=14, decimal_places=2
    )

    selling_price: Decimal = Field(
        ge=0, max_digits=14, decimal_places=2
    )

    unit: str = Field(min_length=1, max_length=30)


class ProductCreate(ProductBase):
    stock_quantity: int = Field(default=0, ge=0)


class ProductUpdate(BaseModel):
    name: str | None = Field(
        default=None, min_length=1, max_length=150
    )

    cost_price: Decimal | None = Field(
        default=None, ge=0,
        max_digits=14, decimal_places=2
    )

    selling_price: Decimal | None = Field(
        default=None, ge=0,
        max_digits=14, decimal_places=2
    )

    unit: str | None = Field(
        default=None, min_length=1, max_length=30
    )


class ProductResponse(ProductBase):
    id: UUID
    shop_id: UUID
    stock_quantity: int
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)



class StockAdjustment(BaseModel):
    quantity: int

    @field_validator("quantity")
    @classmethod
    def validate_quantity(cls, value: int) -> int:
        if value == 0:
            raise ValueError("Quantity cannot be zero")

        return value