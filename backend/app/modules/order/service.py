from fastapi import HTTPException
from .models import Order,PaymentStatus

from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from .models import Customer,CustomerOrder, Order,CustomerOrderStatus,Order,TraderOrder
from backend.app.modules.shop.models import Shop
from backend.app.modules.trader.models import Trader





def calculate_payment_status(bill_amount, paid_amount):
    if paid_amount <= 0:
        return PaymentStatus.NOT_PAID

    if paid_amount >= bill_amount:
        return PaymentStatus.PAID

    return PaymentStatus.PARTIALLY_PAID


def validate_payment(bill_amount, paid_amount):
    if bill_amount <= 0:
        raise HTTPException(400, "Bill amount must be positive")

    if paid_amount < 0:
        raise HTTPException(400, "Paid amount cannot be negative")

    if paid_amount > bill_amount:
        raise HTTPException(
            400,
            "Paid amount cannot exceed bill amount",
        )


def build_order(order_data):
    paid_amount = order_data.paid_amount

    validate_payment(
        order_data.bill_amount,
        paid_amount,
    )

    return Order(
        date=order_data.date,
        timestamp=order_data.timestamp,
        bill_amount=order_data.bill_amount,
        paid_amount=paid_amount,
        meta_data=order_data.meta_data,
        payment_status=calculate_payment_status(
            order_data.bill_amount,
            paid_amount,
        ),
    )




def verify_owner_or_customer(current_owner, phone_number):
    if current_owner is None and not phone_number:
        raise HTTPException(
            401,
            "Customer mobile number is required",
        )


async def resolve_customer(
    db: AsyncSession,
    current_owner,
    customer_id=None,
    phone_number=None,
):
    if current_owner is not None:
        if customer_id:
            result = await db.execute(
                select(Customer).where(Customer.id == customer_id)
            )
        elif phone_number:
            result = await db.execute(
                select(Customer).where(
                    Customer.phone_number == phone_number
                )
            )
        else:
            raise HTTPException(
                400,
                "customer_id or phone_number is required",
            )

    else:
        verify_owner_or_customer(None, phone_number)

        result = await db.execute(
            select(Customer).where(
                Customer.phone_number == phone_number
            )
        )

    customer = result.scalar_one_or_none()

    if not customer:
        raise HTTPException(404, "Customer not found")

    return customer


async def get_customer_orders(
    db: AsyncSession,
    current_owner,
    phone_number=None,
    customer_id=None,
    order_id=None,
    order_status=None,
    branch_address=None,
    payment_status=None,
):
    # Customer access is limited to their own phone number.
    if current_owner is None:
        if not phone_number:
            raise HTTPException(
                401,
                "Customer mobile number is required",
            )

        customer = await resolve_customer(
            db,
            None,
            phone_number=phone_number,
        )

        query = select(CustomerOrder).where(
            CustomerOrder.customer_id == customer.id
        )

    else:
        query = select(CustomerOrder)

        if customer_id:
            query = query.where(
                CustomerOrder.customer_id == customer_id
            )

    query = query.options(
        selectinload(CustomerOrder.order),
    )

    if order_id:
        query = query.where(
            CustomerOrder.order_id == order_id
        )

    if order_status:
        query = query.where(
            CustomerOrder.order_status == order_status
        )

    if current_owner is not None and payment_status:
        query = query.join(
            Order,
            CustomerOrder.order_id == Order.id,
        ).where(
            Order.payment_status == payment_status
        )

    if current_owner is not None and branch_address:
        query = query.join(
            Shop,
            CustomerOrder.shop_id == Shop.id,
        ).where(
            Shop.branch_address.ilike(
                f"%{branch_address}%"
            )
        )

    result = await db.execute(query)
    orders = result.scalars().unique().all()

    if order_id:
        if not orders:
            raise HTTPException(404, "Order not found")

        return orders[0]

    return orders


async def create_customer_order(
    db: AsyncSession,
    current_owner,
    order_data,
):
    customer = await resolve_customer(
        db,
        current_owner,
        customer_id=order_data.customer_id,
        phone_number=order_data.phone_number,
    )

    # Customers cannot choose another customer's identity.
    order = build_order(order_data.order)

    customer_order = CustomerOrder(
        order=order,
        customer_id=customer.id,
        shop_id=order_data.shop_id,
        selling_item_ids=order_data.selling_item_ids,
        transaction_ids=order_data.transaction_ids,
        order_status=CustomerOrderStatus.CONFIRMED,
    )

    db.add(customer_order)

    await db.commit()

    result = await db.execute(
        select(CustomerOrder)
        .where(CustomerOrder.order_id == order.id)
        .options(selectinload(CustomerOrder.order))
    )

    return result.scalar_one()


async def update_customer_order(
    db: AsyncSession,
    current_owner,
    order_id: str,
    phone_number: str | None,
    new_status: CustomerOrderStatus,
):
    query = (
        select(CustomerOrder)
        .where(CustomerOrder.order_id == order_id)
        .options(selectinload(CustomerOrder.order))
    )

    if current_owner is None:
        customer = await resolve_customer(
            db,
            None,
            phone_number=phone_number,
        )

        query = query.where(
            CustomerOrder.customer_id == customer.id
        )

        # Customer can only request cancellation.
        if new_status != CustomerOrderStatus.CANCELLED:
            raise HTTPException(
                403,
                "Customers can only cancel their orders",
            )

    result = await db.execute(query)
    customer_order = result.scalar_one_or_none()

    if not customer_order:
        raise HTTPException(
            404,
            "Order not found or access denied",
        )

    if current_owner is not None:
        if (
            customer_order.order_status
            in {
                CustomerOrderStatus.HANDED_OVER,
                CustomerOrderStatus.CANCELLED,
            }
            and customer_order.order_status != new_status
        ):
            raise HTTPException(
                409,
                "Cannot change a completed or cancelled order",
            )

    customer_order.order_status = new_status

    await db.commit()
    await db.refresh(customer_order)

    return customer_order


async def delete_customer_order(
    db: AsyncSession,
    order_id: str,
):
    result = await db.execute(
        select(CustomerOrder)
        .where(CustomerOrder.order_id == order_id)
        .options(selectinload(CustomerOrder.order))
    )

    customer_order = result.scalar_one_or_none()

    if not customer_order:
        raise HTTPException(404, "Order not found")

    # Restrict deletion when items or transactions exist.
    if (
        customer_order.selling_item_ids
        or customer_order.transaction_ids
    ):
        raise HTTPException(
            409,
            "Cannot delete an order containing items or transactions",
        )

    await db.delete(customer_order)
    await db.commit()

    return {"message":"Deleted successfully"}




async def get_trader_orders(
    db: AsyncSession,
    trader_name=None,
    trader_phone_number=None,
    start_date=None,
    end_date=None,
    payment_status=None,
    business_name=None,
):
    query = (
        select(TraderOrder)
        .join(Order)
        .join(Trader)
        .options(
            selectinload(TraderOrder.order),
            selectinload(TraderOrder.trader),
        )
    )

    if trader_name:
        query = query.where(
            Trader.name.ilike(f"%{trader_name}%")
        )

    if trader_phone_number:
        query = query.where(
            Trader.phone_number == trader_phone_number
        )

    if business_name:
        query = query.where(
            Trader.business_name.ilike(f"%{business_name}%")
        )

    if start_date:
        query = query.where(Order.date >= start_date)

    if end_date:
        query = query.where(Order.date <= end_date)

    if payment_status:
        query = query.where(
            Order.payment_status == payment_status
        )

    result = await db.execute(query)

    return result.scalars().unique().all()


async def create_trader_order(
    db: AsyncSession,
    order_data,
):
    result = await db.execute(
        select(Trader).where(
            Trader.id == order_data.trader_id
        )
    )

    trader = result.scalar_one_or_none()

    if not trader:
        raise HTTPException(404, "Trader not found")

    order = build_order(order_data.order)

    trader_order = TraderOrder(
        order=order,
        trader_id=trader.id,
        trader_name=trader.name,
        buying_item_ids=order_data.buying_item_ids,
        transaction_ids=order_data.transaction_ids,
    )

    db.add(trader_order)
    await db.commit()

    result = await db.execute(
        select(TraderOrder)
        .where(TraderOrder.order_id == order.id)
        .options(selectinload(TraderOrder.order))
    )

    return result.scalar_one()


async def update_trader_order(
    db: AsyncSession,
    order_id: str,
    order_data,
):
    result = await db.execute(
        select(TraderOrder)
        .where(TraderOrder.order_id == order_id)
        .options(selectinload(TraderOrder.order))
    )

    trader_order = result.scalar_one_or_none()

    if not trader_order:
        raise HTTPException(404, "Trader order not found")

    updates = order_data.model_dump(exclude_unset=True)

    for field, value in updates.items():
        if field in {
            "trader_name",
            "buying_item_ids",
            "transaction_ids",
        }:
            setattr(trader_order, field, value)

    await db.commit()
    await db.refresh(trader_order)

    return trader_order


async def delete_trader_order(
    db: AsyncSession,
    order_id: str,
):
    result = await db.execute(
        select(TraderOrder)
        .where(TraderOrder.order_id == order_id)
    )

    trader_order = result.scalar_one_or_none()

    if not trader_order:
        raise HTTPException(404, "Trader order not found")

    if (
        trader_order.buying_item_ids
        or trader_order.transaction_ids
    ):
        raise HTTPException(
            409,
            "Cannot delete an order containing items or transactions",
        )

    await db.delete(trader_order)
    await db.commit()

    return {"message":"Successfully Deleted"}