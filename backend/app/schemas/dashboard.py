from uuid import UUID
from datetime import datetime, date
from decimal import Decimal

from pydantic import BaseModel

from app.models.order import OrderStatus
from app.models.payments import PaymentMethod
from app.schemas.payment import PaymentStatus


class DashboardSummary(BaseModel):
    start_date: date
    end_date: date

    total_sales: Decimal
    amount_received: Decimal
    outstanding_amount: Decimal
    total_orders: int


class DashboardOrderResponse(BaseModel):
    order_id: UUID

    customer_id: UUID
    customer_name: str
    customer_mobile: str

    total_amount: Decimal
    amount_paid: Decimal
    amount_due: Decimal

    order_status: OrderStatus
    payment_status: PaymentStatus

    created_at: datetime


class DashboardTransactionResponse(BaseModel):
    payment_id: UUID
    order_id: UUID

    customer_id: UUID
    customer_name: str
    customer_mobile: str

    amount: Decimal
    payment_method: PaymentMethod
    reference: str | None

    created_at: datetime


class DashboardOrdersResponse(BaseModel):
    items: list[DashboardOrderResponse]
    total: int
    limit: int
    offset: int


class DashboardTransactionsResponse(BaseModel):
    items: list[DashboardTransactionResponse]
    total: int
    limit: int
    offset: int