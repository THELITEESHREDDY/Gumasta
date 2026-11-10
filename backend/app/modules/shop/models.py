from sqlalchemy import String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.app.database import Base


class Shop(Base):
    __tablename__ = "shops"

    id: Mapped[str] = mapped_column(
        String,
        primary_key=True,
        nullable=False,
    )

    shop_name: Mapped[str] = mapped_column(
        String,
        nullable=False,
    )

    owner_id: Mapped[str] = mapped_column(
        ForeignKey("owners.id"),
        nullable=False,
        index=True,
    )

    branch_address: Mapped[str] = mapped_column(
        String,
        unique=True,
        nullable=False,
    )

    GST_id: Mapped[str | None] = mapped_column(
        String,
        nullable=True,
    )

    bank_account_number: Mapped[str] = mapped_column(
        String,
        nullable=False,
    )

    IFSC_code: Mapped[str] = mapped_column(
        String,
        nullable=False,
    )

    Payment_mobile_number: Mapped[str] = mapped_column(
        String(10),
        nullable=False,
    )

    owner: Mapped["Owner"] = relationship()