from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from .models import Shop
from backend.app.modules.order.models import CustomerOrder
from .schema import ShopCreate, ShopUpdate


async def get_shops(
    db: AsyncSession,
    shop_id: str | None = None,
):
    query = select(Shop)

    if shop_id:
        query = query.where(Shop.id == shop_id)

    result = await db.execute(query)
    shops = result.scalars().all()

    if shop_id and not shops:
        raise HTTPException(status_code=404, detail="Shop not found")

    return shops[0] if shop_id else shops


async def create_shop(
    db: AsyncSession,
    shop_data: ShopCreate,
    owner_id: str,
):
    shop = Shop(
        **shop_data.model_dump(),
        owner_id=owner_id,
    )

    db.add(shop)

    try:
        await db.commit()
        await db.refresh(shop)
        return shop

    except IntegrityError:
        await db.rollback()
        raise HTTPException(
            status_code=409,
            detail="Shop ID or branch address already exists",
        )


async def update_shop(
    db: AsyncSession,
    shop_id: str,
    shop_data: ShopUpdate,
    owner_id: str,
):
    result = await db.execute(
        select(Shop).where(
            Shop.id == shop_id,
            Shop.owner_id == owner_id,
        )
    )

    shop = result.scalar_one_or_none()

    if not shop:
        raise HTTPException(
            status_code=404,
            detail="Shop not found",
        )

    updates = shop_data.model_dump(exclude_unset=True)

    for field, value in updates.items():
        setattr(shop, field, value)

    try:
        await db.commit()
        await db.refresh(shop)
        return shop

    except IntegrityError:
        await db.rollback()
        raise HTTPException(
            status_code=409,
            detail="Branch address already belongs to another shop",
        )


async def delete_shop(
    db: AsyncSession,
    shop_id: str,
    owner_id: str,
):
    result = await db.execute(
        select(Shop).where(
            Shop.id == shop_id,
            Shop.owner_id == owner_id,
        )
    )

    shop = result.scalar_one_or_none()

    if not shop:
        raise HTTPException(
            status_code=404,
            detail="Shop not found",
        )

    # Prevent deletion if customer orders reference this shop.
    order_result = await db.execute(
        select(CustomerOrder.order_id)
        .where(CustomerOrder.shop_id == shop_id)
        .limit(1)
    )

    if order_result.scalar_one_or_none():
        raise HTTPException(
            status_code=409,
            detail="Cannot delete a shop that has existing orders",
        )

    await db.delete(shop)
    await db.commit()

    return {"message":"Deleted successfully"}