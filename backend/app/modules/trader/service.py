from uuid import uuid4
from datetime import date

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError

from backend.app.modules.order.models import Order
from backend.app.modules.trader.models import Trader
from backend.app.modules.order.models import TraderOrder

from .schema import (
    TraderOrderCreate,
    TraderOrderUpdate,
)



async def get_trader_orders(
    db: AsyncSession,
    trader_name: str | None = None,
    trader_phone_number: str | None = None,
    start_date: date | None = None,
    end_date: date | None = None,
    payment_status=None,
    business_name: str | None = None,
):
    stmt = (
        select(TraderOrder)
        .join(TraderOrder.order)
        .join(TraderOrder.trader)
        .options(selectinload(TraderOrder.order))
    )

    if trader_name:
        stmt = stmt.where(TraderOrder.trader_name.ilike(f"%{trader_name}%"))

    if trader_phone_number:
        stmt = stmt.where(
            Trader.phone_number == trader_phone_number
        )

    if start_date:
        stmt = stmt.where(Order.date >= start_date)

    if end_date:
        stmt = stmt.where(Order.date <= end_date)

    if payment_status:
        stmt = stmt.where(Order.payment_status == payment_status)

    if business_name:
        stmt = stmt.where(
            Trader.business_name.ilike(f"%{business_name}%")
        )

    result = await db.execute(stmt)
    return result.scalars().all()


async def create_trader_order(
    db: AsyncSession,
    order_data: TraderOrderCreate,
):
    trader_result = await db.execute(
        select(Trader).where(
            Trader.id == order_data.trader_id
        )
    )

    trader = trader_result.scalar_one_or_none()

    if not trader:
        raise HTTPException(
            status_code=404,
            detail="Trader not found",
        )

    order = build_order(order_data.order)

    trader_order = TraderOrder(
        order=order,
        trader_id=trader.id,
        trader_name=order_data.trader_name,
        buying_item_ids=order_data.buying_item_ids,
        transaction_ids=order_data.transaction_ids,
    )

    db.add(order)
    db.add(trader_order)

    try:
        await db.commit()
        await db.refresh(trader_order)
        await db.refresh(order)

    except IntegrityError:
        await db.rollback()
        raise HTTPException(
            status_code=409,
            detail="Unable to create trader order",
        )

    return trader_order


async def update_trader_order(
    db: AsyncSession,
    order_id: str,
    order_data: TraderOrderUpdate,
):
    result = await db.execute(
        select(TraderOrder)
        .where(TraderOrder.order_id == order_id)
        .options(selectinload(TraderOrder.order))
    )

    trader_order = result.scalar_one_or_none()

    if not trader_order:
        raise HTTPException(
            status_code=404,
            detail="Trader order not found",
        )

    updates = order_data.model_dump(exclude_unset=True)

    for field, value in updates.items():
        setattr(trader_order, field, value)

    try:
        await db.commit()
        await db.refresh(trader_order)

    except IntegrityError:
        await db.rollback()
        raise HTTPException(
            status_code=409,
            detail="Unable to update trader order",
        )

    return trader_order


async def delete_trader_order(
    db: AsyncSession,
    order_id: str,
):
    result = await db.execute(
        select(TraderOrder)
        .where(TraderOrder.order_id == order_id)
        .options(selectinload(TraderOrder.order))
    )

    trader_order = result.scalar_one_or_none()

    if not trader_order:
        raise HTTPException(
            status_code=404,
            detail="Trader order not found",
        )

    if trader_order.buying_item_ids or trader_order.transaction_ids:
        raise HTTPException(
            status_code=409,
            detail="Cannot delete an order containing item or transaction references",
        )

    # Delete the parent Order; its configured ORM cascade
    # should delete the associated TraderOrder.
    await db.delete(trader_order.order)
    await db.commit()

    return {}