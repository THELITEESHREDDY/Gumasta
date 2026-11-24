import uuid
from datetime import datetime, timezone
from typing import TYPE_CHECKING

from sqlalchemy import (
    String, DateTime, ForeignKey,
    Uuid, UniqueConstraint
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.shop import Shop
    from app.models.order import Order
    

class Customer(Base):
    __tablename__ = "customers"

    __table_args__ = (
        UniqueConstraint(
            "shop_id",
            "mobile",
            name="uq_customer_shop_mobile"
        ),
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

    name: Mapped[str] = mapped_column(String(100))

    mobile: Mapped[str] = mapped_column(String(15))

    alternate_mobile: Mapped[str | None] = mapped_column(
        String(15),
        nullable=True
    )

    address: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True
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
        back_populates="customers"
    )
    orders: Mapped[list["Order"]] = relationship(
        back_populates="customer"
    )