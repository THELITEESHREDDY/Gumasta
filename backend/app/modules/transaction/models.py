import enum

from sqlalchemy import (
    String,
    Float,
    Date,
    Time,
    ForeignKey,
    Enum,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.app.database import Base


class PartyType(str, enum.Enum):
    OWNER = "OWNER"
    CUSTOMER = "CUSTOMER"
    TRADER = "TRADER"


class Transaction(Base):
    __tablename__ = "transactions"

    id: Mapped[str] = mapped_column(
        String,
        primary_key=True,
        nullable=False,
    )

    order_id: Mapped[str] = mapped_column(
        ForeignKey("orders.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    amount: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )

    date: Mapped[Date] = mapped_column(
        Date,
        nullable=False,
        index=True,
    )

    time: Mapped[Time] = mapped_column(
        Time,
        nullable=False,
    )

    sender_type: Mapped[PartyType] = mapped_column(
        Enum(PartyType, name="party_type"),
        nullable=False,
    )

    sender_id: Mapped[str] = mapped_column(
        String,
        nullable=False,
        index=True,
    )

    sender_mobile_number: Mapped[str] = mapped_column(
        String(10),
        nullable=False,
    )

    receiver_type: Mapped[PartyType] = mapped_column(
        Enum(PartyType, name="party_type"),
        nullable=False,
    )

    receiver_id: Mapped[str] = mapped_column(
        String,
        nullable=False,
        index=True,
    )

    receiver_mobile_number: Mapped[str] = mapped_column(
        String(10),
        nullable=False,
    )

    order: Mapped["Order"] = relationship(
        back_populates="transactions",
    )