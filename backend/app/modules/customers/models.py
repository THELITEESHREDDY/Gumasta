from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID


from backend.app.database import Base



class Customer(Base):
    __tablename__ = "customers"

    id: Mapped[str] = mapped_column(
        String,
        primary_key=True,
    )

    name: Mapped[str] = mapped_column(
        String,
        nullable=False
    )

    phone_number: Mapped[str] = mapped_column(
        String(10),
        unique=True,
        nullable=False
    )

    whatsApp_number: Mapped[str] = mapped_column(
        String(10),
        nullable=False
    )

    orders: Mapped[list["CustomerOrder"]] = relationship(
        "CustomerOrder",
        back_populates="customer"
    )