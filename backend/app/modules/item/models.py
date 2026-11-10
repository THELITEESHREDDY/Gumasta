from datetime import date
from decimal import Decimal

from sqlalchemy import Date, String, Float,ForeignKey,Numeric
from sqlalchemy.orm import Mapped, mapped_column

from backend.app.database import Base


class Item(Base):
    __tablename__ = "items"

    id: Mapped[str] = mapped_column(
        String,
        primary_key=True,
        nullable=False,
    )

    name: Mapped[str] = mapped_column(
        String,
        unique=True,
        nullable=False,
        index=True,
    )

    selling_price: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )

    cost_price: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )

    quantity: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        default=0.0,
    )

    updatedAt:Mapped[Date] = mapped_column(
        Date,
        nullable=False,
    )


class ItemHistory(Base):
    __tablename__ = "item_history"

    id: Mapped[str] = mapped_column(primary_key=True)

    item_id: Mapped[str] = mapped_column(
        ForeignKey("items.id"),
        index=True
    )

    item_name: Mapped[str] = mapped_column(String(150))

    selling_price: Mapped[Decimal] = mapped_column(Numeric(12, 2))
    cost_price: Mapped[Decimal] = mapped_column(Numeric(12, 2))

    effective_from: Mapped[date] = mapped_column(Date, nullable=False)
    till_date: Mapped[date | None] = mapped_column(Date, nullable=True)