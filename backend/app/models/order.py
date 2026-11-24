import uuid
from datetime import datetime, timezone
from decimal import Decimal
from enum import Enum
from typing import TYPE_CHECKING

from sqlalchemy import (
    Uuid, ForeignKey, Numeric, DateTime,
    CheckConstraint, Enum as SAEnum
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.shop import Shop
    from app.models.customer import Customer
    from app.models.order_item import OrderItem
    from app.models.payments import Payment


class OrderStatus(str, Enum):
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class Order(Base):
    __tablename__ = "orders"

    __table_args__ = (
        CheckConstraint("total_amount >= 0"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        primary_key=True,
        default=uuid.uuid4
    )

    shop_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("shops.id"),
        index=True
    )

    customer_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("customers.id"),
        index=True
    )

    total_amount: Mapped[Decimal] = mapped_column(
        Numeric(14, 2)
    )

    status: Mapped[OrderStatus] = mapped_column(
        SAEnum(OrderStatus, create_constraint=True),
        default=OrderStatus.COMPLETED
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc)
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc)
    )

    shop: Mapped["Shop"] = relationship(
        back_populates="orders"
    )

    customer: Mapped["Customer"] = relationship(
        back_populates="orders"
    )

    order_items: Mapped[list["OrderItem"]] = relationship(
        back_populates="order"
    )

    payments: Mapped[list["Payment"]] = relationship(
        back_populates="order"
    )