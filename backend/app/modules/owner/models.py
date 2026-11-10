from sqlalchemy import String, Boolean
from sqlalchemy.orm import Mapped, mapped_column

from backend.app.database import Base


class Owner(Base):
    __tablename__ = "owners"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    password: Mapped[str] = mapped_column(String, nullable=False)
    email: Mapped[str] = mapped_column(
        String(255), unique=True, index=True, nullable=False
    )
    is_verified: Mapped[bool] = mapped_column(
        Boolean, default=False, nullable=False
    )
    phone_number: Mapped[str] = mapped_column(
        String(10), unique=True, nullable=False
    )