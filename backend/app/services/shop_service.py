from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.shop import Shop
from app.schemas.shop import ShopCreate, ShopUpdate


class ShopNotFoundError(Exception):
    pass


class InvalidShopUpdateError(Exception):
    pass


async def create_shop(
    db: AsyncSession,
    owner_id: UUID,
    data: ShopCreate
) -> Shop:

    shop = Shop(
        owner_id=owner_id,
        **data.model_dump()
    )

    db.add(shop)

    await db.commit()
    await db.refresh(shop)

    return shop


async def get_shops(
    db: AsyncSession,
    owner_id: UUID
) -> list[Shop]:

    result = await db.execute(
        select(Shop)
        .where(Shop.owner_id == owner_id)
        .order_by(Shop.created_at.desc())
    )

    return list(result.scalars().all())


async def get_shop(
    db: AsyncSession,
    shop_id: UUID,
    owner_id: UUID
) -> Shop:

    result = await db.execute(
        select(Shop).where(
            Shop.id == shop_id,
            Shop.owner_id == owner_id
        )
    )

    shop = result.scalar_one_or_none()

    if shop is None:
        raise ShopNotFoundError()

    return shop


async def update_shop(
    db: AsyncSession,
    shop_id: UUID,
    owner_id: UUID,
    data: ShopUpdate
) -> Shop:

    shop = await get_shop(db, shop_id, owner_id)

    updates = data.model_dump(exclude_unset=True)

    for field in ("name", "address", "contact"):
        if field in updates and updates[field] is None:
            raise InvalidShopUpdateError(
                f"{field} cannot be null"
            )

    for field, value in updates.items():
        setattr(shop, field, value)

    await db.commit()
    await db.refresh(shop)

    return shop