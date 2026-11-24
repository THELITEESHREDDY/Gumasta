import uuid
from datetime import datetime, timezone
from typing import TYPE_CHECKING

from sqlalchemy import String, DateTime, ForeignKey, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.product import Product
    from app.models.customer import Customer
    from app.models.order import Order


class Shop(Base):
    __tablename__ = "shops"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        primary_key=True,
        default=uuid.uuid4
    )

    owner_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id"),
        index=True
    )

    name: Mapped[str] = mapped_column(String(150))

    gst_id: Mapped[str | None] = mapped_column(
        String(15),
        nullable=True
    )

    address: Mapped[str] = mapped_column(String(500))

    contact: Mapped[str] = mapped_column(String(15))

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc)
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc)
    )

    owner: Mapped["User"] = relationship(
        back_populates="shops"
    )

    products: Mapped[list["Product"]] = relationship(
        back_populates="shop"
    )

    customers: Mapped[list["Customer"]] = relationship(
        back_populates="shop"
    )

    orders: Mapped[list["Order"]] = relationship(
        back_populates="shop"
    )