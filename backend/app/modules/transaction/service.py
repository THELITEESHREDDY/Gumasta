from uuid import uuid4
from datetime import date

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from .models import Transaction, PartyType
from backend.app.modules.order.models import Order, PaymentStatus
from backend.app.modules.owner.models import Owner
from backend.app.modules.customers.models import Customer
from backend.app.modules.trader.models import Trader

from backend.app.modules.transaction.schema import TransactionCreate


PARTY_MODELS = {
    PartyType.OWNER: Owner,
    PartyType.CUSTOMER: Customer,
    PartyType.TRADER: Trader,
}


def calculate_payment_status(
    bill_amount: float,
    paid_amount: float,
) -> PaymentStatus:

    if paid_amount == 0:
        return PaymentStatus.NOT_PAID

    if paid_amount >= bill_amount:
        return PaymentStatus.PAID

    return PaymentStatus.PARTIALLY_PAID


async def validate_party(
    db: AsyncSession,
    party_type: PartyType,
    party_id: str,
):
    model = PARTY_MODELS[party_type]

    result = await db.execute(
        select(model).where(model.id == party_id)
    )

    party = result.scalar_one_or_none()

    if not party:
        raise HTTPException(
            status_code=404,
            detail=f"{party_type.value} not found: {party_id}",
        )

    return party


async def get_transactions(
    db: AsyncSession,
    sender_id: str | None = None,
    receiver_id: str | None = None,
    sender_type: PartyType | None = None,
    receiver_type: PartyType | None = None,
    start_date: date | None = None,
    end_date: date | None = None,
):
    if start_date and end_date and start_date > end_date:
        raise HTTPException(
            status_code=422,
            detail="start_date cannot be after end_date",
        )

    stmt = select(Transaction)

    if sender_id:
        stmt = stmt.where(Transaction.sender_id == sender_id)

    if receiver_id:
        stmt = stmt.where(Transaction.receiver_id == receiver_id)

    if sender_type:
        stmt = stmt.where(Transaction.sender_type == sender_type)

    if receiver_type:
        stmt = stmt.where(Transaction.receiver_type == receiver_type)

    if start_date:
        stmt = stmt.where(Transaction.date >= start_date)

    if end_date:
        stmt = stmt.where(Transaction.date <= end_date)

    stmt = stmt.order_by(
        Transaction.date.desc(),
        Transaction.time.desc(),
    )

    result = await db.execute(stmt)

    return result.scalars().all()


async def get_transaction_by_id(
    db: AsyncSession,
    transaction_id: str,
):
    result = await db.execute(
        select(Transaction).where(
            Transaction.id == transaction_id
        )
    )

    transaction = result.scalar_one_or_none()

    if not transaction:
        raise HTTPException(
            status_code=404,
            detail="Transaction not found",
        )

    return transaction


async def create_transaction(
    db: AsyncSession,
    transaction_data: TransactionCreate,
):
    # Validate sender and receiver.
    await validate_party(
        db,
        transaction_data.sender_type,
        transaction_data.sender_id,
    )

    await validate_party(
        db,
        transaction_data.receiver_type,
        transaction_data.receiver_id,
    )

    # Lock the order while updating its payment total.
    result = await db.execute(
        select(Order)
        .where(Order.id == transaction_data.order_id)
        .with_for_update()
    )

    order = result.scalar_one_or_none()

    if not order:
        raise HTTPException(
            status_code=404,
            detail="Order not found",
        )

    new_paid_amount = (
        order.paid_amount + transaction_data.amount
    )

    if new_paid_amount > order.bill_amount:
        raise HTTPException(
            status_code=400,
            detail="Transaction amount exceeds remaining order balance",
        )

    transaction = Transaction(
        id=str(uuid4()),
        order_id=order.id,
        amount=transaction_data.amount,
        date=transaction_data.date,
        time=transaction_data.time,
        sender_type=transaction_data.sender_type,
        sender_id=transaction_data.sender_id,
        sender_mobile_number=transaction_data.sender_mobile_number,
        receiver_type=transaction_data.receiver_type,
        receiver_id=transaction_data.receiver_id,
        receiver_mobile_number=transaction_data.receiver_mobile_number,
    )

    order.paid_amount = new_paid_amount

    order.payment_status = calculate_payment_status(
        order.bill_amount,
        new_paid_amount,
    )

    db.add(transaction)

    try:
        await db.commit()
        await db.refresh(transaction)

    except Exception:
        await db.rollback()
        raise

    return transaction