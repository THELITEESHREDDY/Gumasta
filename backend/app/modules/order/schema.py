from datetime import date, time
from pydantic import BaseModel, Field, ConfigDict

from .models import PaymentStatus,CustomerOrderStatus


class OrderCreate(BaseModel):
    date: date
    timestamp: time
    bill_amount: float = Field(gt=0)
    paid_amount: float = Field(default=0, ge=0)
    meta_data: str | None = None


class OrderResponse(BaseModel):
    id: str
    date: date
    timestamp: time
    bill_amount: float
    paid_amount: float
    meta_data: str | None
    payment_status: PaymentStatus

    model_config = ConfigDict(from_attributes=True)




class CustomerOrderCreate(BaseModel):
    order: OrderCreate

    customer_id: str | None = None
    phone_number: str | None = Field(
        default=None,
        min_length=10,
        max_length=10,
        pattern=r"^\d{10}$",
    )

    shop_id: str = "main"
    selling_item_ids: list[str] = Field(default_factory=list)
    transaction_ids: list[str] = Field(default_factory=list)


class CustomerOrderUpdate(BaseModel):
    order_status: CustomerOrderStatus


class CustomerOrderResponse(BaseModel):
    order_id: str
    customer_id: str
    shop_id: str
    selling_item_ids: list[str]
    transaction_ids: list[str]
    order_status: CustomerOrderStatus
    order: OrderResponse

    model_config = ConfigDict(from_attributes=True)


class TraderOrderCreate(BaseModel):
    order: OrderCreate

    trader_id: str
    trader_name: str

    buying_item_ids: list[str] = Field(default_factory=list)
    transaction_ids: list[str] = Field(default_factory=list)


class TraderOrderUpdate(BaseModel):
    trader_name: str | None = None
    buying_item_ids: list[str] | None = None
    transaction_ids: list[str] | None = None


class TraderOrderResponse(BaseModel):
    order_id: str
    trader_id: str
    trader_name: str
    buying_item_ids: list[str]
    transaction_ids: list[str]
    order: OrderResponse

    model_config = ConfigDict(from_attributes=True)