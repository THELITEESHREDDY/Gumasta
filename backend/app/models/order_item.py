import uuid
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import (
    Uuid, String, ForeignKey,
    Numeric, CheckConstraint
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.order import Order
    from app.models.product import Product


class OrderItem(Base):
    __tablename__ = "order_items"

    __table_args__ = (
        CheckConstraint("quantity > 0"),
        CheckConstraint("unit_price >= 0"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        primary_key=True,
        default=uuid.uuid4
    )

    order_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("orders.id"),
        index=True
    )

    product_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("products.id"),
        index=True
    )

    product_name: Mapped[str] = mapped_column(
        String(150)
    )

    quantity: Mapped[int] = mapped_column()

    unit_price: Mapped[Decimal] = mapped_column(
        Numeric(14, 2)
    )

    order: Mapped["Order"] = relationship(
        back_populates="order_items"
    )

    product: Mapped["Product"] = relationship(
        back_populates="order_items"
    )

    @property
    def subtotal(self) -> Decimal:
        return self.quantity * self.unit_price