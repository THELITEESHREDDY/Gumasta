from uuid import UUID
from datetime import datetime
from decimal import Decimal

from pydantic import (
    BaseModel,
    Field,
    ConfigDict,
    model_validator
)

from app.models.order import OrderStatus


class OrderItemCreate(BaseModel):
    product_id: UUID

    quantity: int = Field(gt=0)

    unit_price: Decimal | None = Field(
        default=None,
        ge=0,
        max_digits=14,
        decimal_places=2
    )


class OrderCreate(BaseModel):
    customer_id: UUID

    order_items: list[OrderItemCreate] = Field(
        min_length=1
    )

    @model_validator(mode="after")
    def validate_unique_products(self):
        product_ids = [
            item.product_id
            for item in self.order_items
        ]

        if len(product_ids) != len(set(product_ids)):
            raise ValueError(
                "Duplicate products are not allowed"
            )

        return self


class OrderItemResponse(BaseModel):
    id: UUID
    product_id: UUID
    product_name: str
    quantity: int
    unit_price: Decimal
    subtotal: Decimal

    model_config = ConfigDict(from_attributes=True)


class OrderResponse(BaseModel):
    id: UUID
    shop_id: UUID
    customer_id: UUID
    total_amount: Decimal
    status: OrderStatus
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class OrderDetailResponse(OrderResponse):
    order_items: list[OrderItemResponse]