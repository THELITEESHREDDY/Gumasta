from uuid import UUID
from decimal import Decimal

from sqlalchemy import select, update, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.order import Order, OrderStatus
from app.models.payments import Payment

from app.schemas.payment import (
    PaymentCreate,
    PaymentSummary,
    PaymentStatus
)

from app.services.order_service import (
    OrderNotFoundError
)


class InvalidPaymentError(Exception):
    pass


class OverpaymentError(Exception):
    pass


async def get_payment_order(
    db: AsyncSession,
    shop_id: UUID,
    order_id: UUID
) -> Order:

    result = await db.execute(
        select(Order).where(
            Order.id == order_id,
            Order.shop_id == shop_id
        )
    )

    order = result.scalar_one_or_none()

    if order is None:
        raise OrderNotFoundError()

    return order

async def get_amount_paid(
    db: AsyncSession,
    order_id: UUID
) -> Decimal:

    result = await db.execute(
        select(
            func.coalesce(
                func.sum(Payment.amount), 0
            )
        ).where(
            Payment.order_id == order_id
        )
    )

    return Decimal(result.scalar_one()).quantize(
        Decimal("0.01")
    )

async def get_payment_summary(
    db: AsyncSession,
    shop_id: UUID,
    order_id: UUID
) -> PaymentSummary:

    order = await get_payment_order(
        db, shop_id, order_id
    )

    amount_paid = await get_amount_paid(
        db, order_id
    )

    amount_due = order.total_amount - amount_paid

    if order.status == OrderStatus.CANCELLED:

        payment_status = PaymentStatus.CANCELLED
        amount_due = Decimal("0.00")

    elif amount_due == 0:

        payment_status = PaymentStatus.PAID

    elif amount_paid == 0:

        payment_status = PaymentStatus.UNPAID

    else:

        payment_status = PaymentStatus.PARTIALLY_PAID

    return PaymentSummary(
        order_id=order.id,
        total_amount=order.total_amount,
        amount_paid=amount_paid,
        amount_due=amount_due,
        payment_status=payment_status
    )

async def lock_order_for_payment(
    db: AsyncSession,
    shop_id: UUID,
    order_id: UUID
) -> Order:

    statement = (
        update(Order)
        .where(
            Order.id == order_id,
            Order.shop_id == shop_id,
            Order.status == OrderStatus.COMPLETED
        )
        .values(
            status=Order.status
        )
        .returning(Order)
        .execution_options(populate_existing=True)
    )

    result = await db.execute(statement)

    order = result.scalar_one_or_none()

    if order is None:

        await get_payment_order(
            db, shop_id, order_id
        )

        raise InvalidPaymentError(
            "Cannot record payment for a cancelled order"
        )

    return order

async def create_payment(
    db: AsyncSession,
    shop_id: UUID,
    order_id: UUID,
    data: PaymentCreate
) -> Payment:

    try:

        order = await lock_order_for_payment(
            db, shop_id, order_id
        )

        amount_paid = await get_amount_paid(
            db, order_id
        )

        amount_due = order.total_amount - amount_paid

        if data.amount > amount_due:
            raise OverpaymentError(
                f"Payment exceeds outstanding balance. "
                f"Amount due: {amount_due}"
            )

        payment = Payment(
            order_id=order_id,
            **data.model_dump()
        )

        db.add(payment)

        await db.commit()

    except Exception:
        await db.rollback()
        raise

    await db.refresh(payment)

    return payment


async def get_payments(
    db: AsyncSession,
    shop_id: UUID,
    order_id: UUID
) -> list[Payment]:

    await get_payment_order(
        db, shop_id, order_id
    )

    result = await db.execute(
        select(Payment)
        .where(
            Payment.order_id == order_id
        )
        .order_by(
            Payment.created_at.desc(),
            Payment.id.desc()
        )
    )

    return list(result.scalars().all())