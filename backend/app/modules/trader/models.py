from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from backend.app.database import Base


class Trader(Base):
    __tablename__ = "traders"

    id: Mapped[str] = mapped_column(
        String,
        primary_key=True,
        nullable=False,
    )

    name: Mapped[str] = mapped_column(
        String,
        nullable=False,
        index=True,
    )

    phone_number: Mapped[str] = mapped_column(
        String(10),
        nullable=False,
        index=True,
    )

    account_number: Mapped[str] = mapped_column(
        String,
        nullable=False,
    )

    ifsc_code: Mapped[str] = mapped_column(
        String(11),
        nullable=False,
    )

    business_name: Mapped[str] = mapped_column(
        String,
        nullable=False,
        index=True,
    )