import enum
import uuid
from datetime import date, time
from typing import List
from sqlalchemy import ForeignKey, String, Date, Time, Float, Text, Enum, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.app.database import Base
from backend.app.modules.customers.models import Customer
from backend.app.modules.trader.models import Trader


class PaymentStatus(str, enum.Enum):
    NOT_PAID = "NOT PAID"
    PAID = "PAID"
    PARTIALLY_PAID = "PARTIALLY PAID"


class CustomerOrderStatus(str, enum.Enum):
    CONFIRMED = "confirmed"
    PROCESSING = "processing"
    SHIPPED = "shipped"
    HANDED_OVER = "Handed over"
    CANCELLED = "cancelled"



class Order(Base):
    __tablename__ = "orders"

    id: Mapped[str] = mapped_column(
        String,
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
    )

    date: Mapped[date] = mapped_column(
        Date,
        nullable=False,
    )

    timestamp: Mapped[time] = mapped_column(
        Time,
        nullable=False,
    )

    bill_amount: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )

    paid_amount: Mapped[float] = mapped_column(
        Float,
        default=0.0,
        nullable=False,
    )

    meta_data: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    payment_status: Mapped[PaymentStatus] = mapped_column(
        Enum(PaymentStatus),
        nullable=False,
        default=PaymentStatus.NOT_PAID,
    )

    customer_order: Mapped["CustomerOrder | None"] = relationship(
        back_populates="order",
        uselist=False,
        cascade="all, delete-orphan",
    )

    trader_order: Mapped["TraderOrder | None"] = relationship(
        back_populates="order",
        uselist=False,
        cascade="all, delete-orphan",
    )





class CustomerOrderItem(Base):
    __tablename__ = "customer_order_items"

    id: Mapped[str] = mapped_column(
        String,
        primary_key=True,
    )

    order_id: Mapped[str] = mapped_column(
        ForeignKey("customer_orders.order_id"),
        nullable=False,
        index=True,
    )

    item_id: Mapped[str | None] = mapped_column(
        String,
        nullable=True,
    )

    item_name: Mapped[str] = mapped_column(
        String,
        nullable=False,
    )

    quantity: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )

    unit_selling_price: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )

    unit_cost_price: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )

    line_total: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )

    customer_order: Mapped["CustomerOrder"] = relationship(
        back_populates="selling_items"
    )



class TraderOrderItem(Base):
    __tablename__ = "trader_order_items"

    id: Mapped[str] = mapped_column(
        String,
        primary_key=True,
    )

    order_id: Mapped[str] = mapped_column(
        ForeignKey("customer_orders.order_id"),
        nullable=False,
        index=True,
    )

    item_id: Mapped[str | None] = mapped_column(
        String,
        nullable=True,
    )

    item_name: Mapped[str] = mapped_column(
        String,
        nullable=False,
    )

    quantity: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )

    unit_purchase_price: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )

    line_total: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )

    trader_order: Mapped["TraderOrder"] = relationship(
        back_populates="buying_items"
    )


class CustomerOrder(Base):
    __tablename__ = "customer_orders"

    order_id: Mapped[str] = mapped_column(
        ForeignKey("orders.id", ondelete="CASCADE"),
        primary_key=True,
    )

    customer_id: Mapped[str] = mapped_column(
        ForeignKey("customers.id"),
        nullable=False,
        index=True,
    )

    shop_id: Mapped[str] = mapped_column(
        ForeignKey("shops.id"),
        nullable=False,
        index=True,
    )

    
    selling_items: Mapped[list["CustomerOrderItem"]] = relationship(
        back_populates="customer_order",
        cascade="all, delete-orphan",
    )



    order_status: Mapped[CustomerOrderStatus] = mapped_column(
        Enum(CustomerOrderStatus),
        default=CustomerOrderStatus.CONFIRMED,
        nullable=False,
    )

    order: Mapped["Order"] = relationship(
        back_populates="customer_order",
    )

    customer: Mapped["Customer"] = relationship(
        back_populates="orders",
    )





class TraderOrder(Base):
    __tablename__ = "trader_orders"

    order_id: Mapped[str] = mapped_column(
        ForeignKey("orders.id", ondelete="CASCADE"),
        primary_key=True,
    )

    trader_id: Mapped[str] = mapped_column(
        ForeignKey("traders.id"),
        nullable=False,
        index=True,
    )

    trader_name: Mapped[str] = mapped_column(
        String,
        nullable=False,
    )

    # List of buying item IDs
    buying_item: Mapped[List[TraderOrderItem]] = relationship(
        back_populates="trader_order",
        cascade="all, delete-orphan",
    )

    order: Mapped["Order"] = relationship(
        back_populates="trader_order",
    )

    trader: Mapped["Trader"] = relationship()
