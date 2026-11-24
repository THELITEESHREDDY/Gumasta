import uuid
from datetime import datetime, timezone
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import (
    String, DateTime, ForeignKey,
    Uuid, Numeric, CheckConstraint
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.shop import Shop
    from app.models.order_item import OrderItem


class Product(Base):
    __tablename__ = "products"

    __table_args__ = (
        CheckConstraint("cost_price >= 0"),
        CheckConstraint("selling_price >= 0"),
        CheckConstraint("stock_quantity >= 0"),
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

    name: Mapped[str] = mapped_column(String(150))

    cost_price: Mapped[Decimal] = mapped_column(
        Numeric(14, 2)
    )

    selling_price: Mapped[Decimal] = mapped_column(
        Numeric(14, 2)
    )

    stock_quantity: Mapped[int] = mapped_column(default=0)

    unit: Mapped[str] = mapped_column(String(30))

    is_active: Mapped[bool] = mapped_column(default=True)

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
        back_populates="products"
    )

    order_items: Mapped[list["OrderItem"]] = relationship(
        back_populates="product"
    )