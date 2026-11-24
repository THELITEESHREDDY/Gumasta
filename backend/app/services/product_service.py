from uuid import UUID

from sqlalchemy import select,update
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.product import StockAdjustment
from app.models.product import Product
from app.schemas.product import ProductCreate, ProductUpdate


class ProductNotFoundError(Exception):
    pass


class InvalidProductUpdateError(Exception):
    pass


class InsufficientStockError(Exception):
    pass



async def create_product(
    db: AsyncSession,
    shop_id: UUID,
    data: ProductCreate
) -> Product:

    product = Product(
        shop_id=shop_id,
        **data.model_dump()
    )

    db.add(product)

    await db.commit()
    await db.refresh(product)

    return product


async def get_products(
    db: AsyncSession,
    shop_id: UUID,
    include_inactive: bool = False
) -> list[Product]:

    query = select(Product).where(
        Product.shop_id == shop_id
    )

    if not include_inactive:
        query = query.where(
            Product.is_active.is_(True)
        )

    query = query.order_by(Product.name)

    result = await db.execute(query)

    return list(result.scalars().all())


async def get_product(
    db: AsyncSession,
    shop_id: UUID,
    product_id: UUID
) -> Product:

    result = await db.execute(
        select(Product).where(
            Product.id == product_id,
            Product.shop_id == shop_id
        )
    )

    product = result.scalar_one_or_none()

    if product is None:
        raise ProductNotFoundError()

    return product


async def update_product(
    db: AsyncSession,
    shop_id: UUID,
    product_id: UUID,
    data: ProductUpdate
) -> Product:

    product = await get_product(
        db, shop_id, product_id
    )

    if not product.is_active:
        raise InvalidProductUpdateError(
            "Product is inactive"
        )

    updates = data.model_dump(exclude_unset=True)

    for field, value in updates.items():
        if value is None:
            raise InvalidProductUpdateError(
                f"{field} cannot be null"
            )

    for field, value in updates.items():
        setattr(product, field, value)

    await db.commit()
    await db.refresh(product)

    return product



async def deactivate_product(
    db: AsyncSession,
    shop_id: UUID,
    product_id: UUID
) -> None:

    product = await get_product(
        db, shop_id, product_id
    )

    if not product.is_active:
        return

    product.is_active = False

    await db.commit()


async def adjust_stock(
    db: AsyncSession,
    shop_id: UUID,
    product_id: UUID,
    data: StockAdjustment
) -> Product:

    statement = (
        update(Product)
        .where(
            Product.id == product_id,
            Product.shop_id == shop_id,
            Product.is_active.is_(True),
            Product.stock_quantity + data.quantity >= 0
        )
        .values(
            stock_quantity=Product.stock_quantity + data.quantity
        )
        .returning(Product)
    )

    result = await db.execute(statement)

    product = result.scalar_one_or_none()

    if product is None:
        existing_product = await get_product(
            db, shop_id, product_id
        )

        if not existing_product.is_active:
            raise InvalidProductUpdateError(
                "Product is inactive"
            )

        raise InsufficientStockError(
            "Insufficient stock"
        )

    await db.commit()
    await db.refresh(product)

    return product