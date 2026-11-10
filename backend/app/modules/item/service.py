from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import uuid4
from datetime import date

from .models import Item,ItemHistory
from backend.app.modules.order.models import CustomerOrder,TraderOrder
from .schema import ItemCreate, ItemUpdate


async def get_items(
    db: AsyncSession,
    item_name: str | None = None,
    item_id: str | None = None,
):
    query = select(Item)

    if item_id:
        query = query.where(Item.id == item_id)

    if item_name:
        query = query.where(Item.name.ilike(item_name))

    result = await db.execute(query)
    items = result.scalars().all()

    if item_id or item_name:
        if not items:
            raise HTTPException(
                status_code=404,
                detail="Item not found",
            )

        return items[0]

    return items


async def create_item(
    db: AsyncSession,
    item_data: ItemCreate,
):
    item = Item(**item_data.model_dump())

    db.add(item)

    try:
        await db.commit()
        await db.refresh(item)

    except IntegrityError:
        await db.rollback()
        raise HTTPException(
            status_code=409,
            detail="Item ID or name already exists",
        )

    return item


async def update_item(
    db: AsyncSession,
    item_id: str,
    item_data: ItemUpdate,
):
    result = await db.execute(
        select(Item).where(Item.id == item_id)
    )

    item = result.scalar_one_or_none()

    if not item:
        raise HTTPException(
            status_code=404,
            detail="Item not found",
        )

    prev_item = ItemHistory(
        id= str(uuid4()),
        item_id=item.id,
        item_name=item.name,
        selling_price = item.selling_price,
        cost_price = item.cost_price,
        effective_from= item.updatedAt,
        till_date = date.today()
    )
    updates = item_data.model_dump(exclude_unset=True)
    
    for field, value in updates.items():
        setattr(item, field, value)

    try:
        await db.add(prev_item)
        await db.commit()
        await db.refresh(item)
        await db.refresh(prev_item)



    except IntegrityError:
        await db.rollback()
        raise HTTPException(
            status_code=409,
            detail="Item name already exists",
        )

    return item


async def delete_item(
    db: AsyncSession,
    item_id: str,
):
    result = await db.execute(
        select(Item).where(Item.id == item_id)
    )

    item = result.scalar_one_or_none()

    if not item:
        raise HTTPException(
            status_code=404,
            detail="Item not found",
        )

    # Item IDs are stored in JSON arrays, not foreign keys.
    # Therefore, check existing orders before deletion.

    customer_orders = await db.execute(
        select(CustomerOrder.selling_item_ids)
    )

    trader_orders = await db.execute(
        select(TraderOrder.buying_item_ids)
    )

    is_used_in_customer_orders = any(
        item_id in (item_ids or [])
        for item_ids in customer_orders.scalars().all()
    )

    is_used_in_trader_orders = any(
        item_id in (item_ids or [])
        for item_ids in trader_orders.scalars().all()
    )

    if is_used_in_customer_orders or is_used_in_trader_orders:
        raise HTTPException(
            status_code=409,
            detail="Cannot delete item because it is referenced by existing orders",
        )

    await db.delete(item)
    await db.commit()

    return {"message":"Deleted Successfully"}