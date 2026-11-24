from uuid import UUID
from decimal import Decimal
from datetime import date, datetime, time, timedelta, timezone

from sqlalchemy import select, update
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.order import Order, OrderStatus
from app.models.order_item import OrderItem
from app.models.product import Product
from app.models.customer import Customer
from app.models.payments import Payment

from app.schemas.order import OrderCreate


class OrderNotFoundError(Exception):
    pass


class InvalidOrderError(Exception):
    pass


class InsufficientStockError(Exception):
    pass


class OrderCancellationError(Exception):
    pass


async def validate_customer(
    db: AsyncSession,
    shop_id: UUID,
    customer_id: UUID
) -> None:

    result = await db.execute(
        select(Customer.id).where(
            Customer.id == customer_id,
            Customer.shop_id == shop_id
        )
    )

    if result.scalar_one_or_none() is None:
        raise InvalidOrderError(
            "Customer not found in this shop"
        )

async def deduct_product_stock(
    db: AsyncSession,
    shop_id: UUID,
    product_id: UUID,
    quantity: int
) -> Product:

    statement = (
        update(Product)
        .where(
            Product.id == product_id,
            Product.shop_id == shop_id,
            Product.is_active.is_(True),
            Product.stock_quantity >= quantity
        )
        .values(
            stock_quantity=Product.stock_quantity - quantity
        )
        .returning(Product)
    )

    result = await db.execute(statement)

    product = result.scalar_one_or_none()

    if product is not None:
        return product

    result = await db.execute(
        select(Product).where(
            Product.id == product_id,
            Product.shop_id == shop_id
        )
    )

    product = result.scalar_one_or_none()

    if product is None:
        raise InvalidOrderError(
            f"Product {product_id} not found in this shop"
        )

    if not product.is_active:
        raise InvalidOrderError(
            f"Product {product.name} is inactive"
        )

    raise InsufficientStockError(
        f"Insufficient stock for {product.name}. "
        f"Available: {product.stock_quantity}, "
        f"Requested: {quantity}"
    )


async def get_order(
    db: AsyncSession,
    shop_id: UUID,
    order_id: UUID
) -> Order:

    result = await db.execute(
        select(Order)
        .options(
            selectinload(Order.order_items)
        )
        .where(
            Order.id == order_id,
            Order.shop_id == shop_id
        )
    )

    order = result.scalar_one_or_none()

    if order is None:
        raise OrderNotFoundError()

    return order


async def create_order(
    db: AsyncSession,
    shop_id: UUID,
    data: OrderCreate
) -> Order:

    try:
        await validate_customer(
            db,
            shop_id,
            data.customer_id
        )

        order = Order(
            shop_id=shop_id,
            customer_id=data.customer_id,
            total_amount=Decimal("0.00"),
            status=OrderStatus.COMPLETED
        )

        db.add(order)

        await db.flush()

        total_amount = Decimal("0.00")

        for item in sorted(
            data.order_items,
            key=lambda item: item.product_id
        ):

            product = await deduct_product_stock(
                db=db,
                shop_id=shop_id,
                product_id=item.product_id,
                quantity=item.quantity
            )

            unit_price = (
                item.unit_price
                if item.unit_price is not None
                else product.selling_price
            )

            order_item = OrderItem(
                order_id=order.id,
                product_id=product.id,
                product_name=product.name,
                quantity=item.quantity,
                unit_price=unit_price
            )

            db.add(order_item)

            total_amount += unit_price * item.quantity

        if total_amount > Decimal("999999999999.99"):
            raise InvalidOrderError(
                "Order total exceeds maximum allowed amount"
            )

        order.total_amount = total_amount

        order_id = order.id

        await db.commit()

    except Exception:
        await db.rollback()
        raise

    return await get_order(
        db=db,
        shop_id=shop_id,
        order_id=order_id
    )


async def get_orders(
    db: AsyncSession,
    shop_id: UUID,
    start_date: date | None = None,
    end_date: date | None = None,
    customer_id: UUID | None = None,
    status: OrderStatus | None = None
) -> list[Order]:

    if start_date and end_date and start_date > end_date:
        raise InvalidOrderError(
            "Start date cannot be after end date"
        )

    query = select(Order).where(
        Order.shop_id == shop_id
    )

    if start_date is not None:

        start_datetime = datetime.combine(
            start_date,
            time.min,
            tzinfo=timezone.utc
        )

        query = query.where(
            Order.created_at >= start_datetime
        )

    if end_date is not None:

        end_datetime = datetime.combine(
            end_date + timedelta(days=1),
            time.min,
            tzinfo=timezone.utc
        )

        query = query.where(
            Order.created_at < end_datetime
        )

    if customer_id is not None:

        query = query.where(
            Order.customer_id == customer_id
        )

    if status is not None:

        query = query.where(
            Order.status == status
        )

    query = query.order_by(
        Order.created_at.desc(),
        Order.id.desc()
    )

    result = await db.execute(query)

    return list(result.scalars().all())


async def cancel_order(
    db: AsyncSession,
    shop_id: UUID,
    order_id: UUID
) -> Order:

    try:
        statement = (
            update(Order)
            .where(
                Order.id == order_id,
                Order.shop_id == shop_id,
                Order.status == OrderStatus.COMPLETED,
                ~select(Payment.id)
                .where(Payment.order_id == Order.id)
                .exists()
            )
            .values(status=OrderStatus.CANCELLED)
            .returning(Order.id)
        )

        result = await db.execute(statement)

        cancelled_order_id = result.scalar_one_or_none()

        if cancelled_order_id is None:

            order = await get_order(
                db, shop_id, order_id
            )

            if order.status == OrderStatus.CANCELLED:
                raise OrderCancellationError(
                    "Order is already cancelled"
                )

            raise OrderCancellationError(
                "Cannot cancel an order with existing payments"
            )

        order = await get_order(
            db, shop_id, order_id
        )

        for item in sorted(
            order.order_items,
            key=lambda item: item.product_id
        ):

            result = await db.execute(
                update(Product)
                .where(
                    Product.id == item.product_id,
                    Product.shop_id == shop_id
                )
                .values(
                    stock_quantity=(
                        Product.stock_quantity + item.quantity
                    )
                )
                .returning(Product.id)
            )

            if result.scalar_one_or_none() is None:
                raise OrderCancellationError(
                    "Failed to restore product stock"
                )

        await db.commit()

    except Exception:
        await db.rollback()
        raise

    return await get_order(
        db, shop_id, order_id
    )