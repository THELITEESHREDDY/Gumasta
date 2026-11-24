from uuid import UUID
from decimal import Decimal
from datetime import (
    date,
    datetime,
    time,
    timedelta,
    timezone
)
from sqlalchemy import or_

from app.schemas.dashboard import (
    DashboardOrderResponse,
    DashboardOrdersResponse,
    DashboardTransactionResponse,
    DashboardTransactionsResponse
)

from app.schemas.payment import PaymentStatus

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.order import Order, OrderStatus
from app.models.payments import Payment
from app.models.customer import Customer

from app.schemas.dashboard import DashboardSummary


IST = timezone(timedelta(hours=5, minutes=30))


class InvalidDateRangeError(Exception):
    pass


def resolve_date_range(
    start_date: date | None = None,
    end_date: date | None = None
) -> tuple[date, date, datetime, datetime]:

    today = datetime.now(IST).date()

    start_date = start_date or today
    end_date = end_date or today

    if start_date > end_date:
        raise InvalidDateRangeError(
            "Start date cannot be after end date"
        )

    if end_date == date.max:
        raise InvalidDateRangeError(
            "End date exceeds supported range"
        )

    start_datetime = datetime.combine(
        start_date,
        time.min,
        tzinfo=IST
    ).astimezone(timezone.utc)

    end_datetime = datetime.combine(
        end_date + timedelta(days=1),
        time.min,
        tzinfo=IST
    ).astimezone(timezone.utc)

    return (
        start_date,
        end_date,
        start_datetime,
        end_datetime
    )

async def get_dashboard_summary(
    db: AsyncSession,
    shop_id: UUID,
    start_date: date | None = None,
    end_date: date | None = None
) -> DashboardSummary:

    (
        start_date,
        end_date,
        start_datetime,
        end_datetime
    ) = resolve_date_range(start_date, end_date)

    # 1. Total sales and order count within date range.

    sales_query = select(
        func.coalesce(func.sum(Order.total_amount), 0),
        func.count(Order.id)
    ).where(
        Order.shop_id == shop_id,
        Order.status == OrderStatus.COMPLETED,
        Order.created_at >= start_datetime,
        Order.created_at < end_datetime
    )

    result = await db.execute(sales_query)

    total_sales, total_orders = result.one()

    # 2. Payments received within date range.

    received_query = (
        select(
            func.coalesce(func.sum(Payment.amount), 0)
        )
        .join(Order, Payment.order_id == Order.id)
        .where(
            Order.shop_id == shop_id,
            Order.status == OrderStatus.COMPLETED,
            Payment.created_at >= start_datetime,
            Payment.created_at < end_datetime
        )
    )

    result = await db.execute(received_query)

    amount_received = result.scalar_one()

    # 3. Aggregate lifetime payments per order.

    payment_totals = (
        select(
            Payment.order_id,
            func.sum(Payment.amount).label("amount_paid")
        )
        .join(Order, Payment.order_id == Order.id)
        .where(Order.shop_id == shop_id)
        .group_by(Payment.order_id)
        .subquery()
    )

    # 4. Outstanding balance across all completed orders.

    outstanding_query = (
        select(
            func.coalesce(
                func.sum(
                    Order.total_amount
                    - func.coalesce(
                        payment_totals.c.amount_paid, 0
                    )
                ),
                0
            )
        )
        .outerjoin(
            payment_totals,
            Order.id == payment_totals.c.order_id
        )
        .where(
            Order.shop_id == shop_id,
            Order.status == OrderStatus.COMPLETED
        )
    )

    result = await db.execute(outstanding_query)

    outstanding_amount = result.scalar_one()

    return DashboardSummary(
        start_date=start_date,
        end_date=end_date,
        total_sales=Decimal(total_sales).quantize(
            Decimal("0.01")
        ),
        amount_received=Decimal(amount_received).quantize(
            Decimal("0.01")
        ),
        outstanding_amount=Decimal(
            outstanding_amount
        ).quantize(Decimal("0.01")),
        total_orders=total_orders
    )


def calculate_payment_status(
    order_status: OrderStatus,
    total_amount: Decimal,
    amount_paid: Decimal
) -> tuple[Decimal, PaymentStatus]:

    if order_status == OrderStatus.CANCELLED:
        return Decimal("0.00"), PaymentStatus.CANCELLED

    amount_due = total_amount - amount_paid

    if amount_due == 0:
        return amount_due, PaymentStatus.PAID

    if amount_paid == 0:
        return amount_due, PaymentStatus.UNPAID

    return amount_due, PaymentStatus.PARTIALLY_PAID


async def get_dashboard_orders(
    db: AsyncSession,
    shop_id: UUID,
    start_date: date | None = None,
    end_date: date | None = None,
    search: str | None = None,
    limit: int = 20,
    offset: int = 0
) -> DashboardOrdersResponse:

    (
        start_date,
        end_date,
        start_datetime,
        end_datetime
    ) = resolve_date_range(start_date, end_date)

    # Aggregate payments per order.
    payment_totals = (
        select(
            Payment.order_id,
            func.sum(Payment.amount).label("amount_paid")
        )
        .join(Order, Payment.order_id == Order.id)
        .where(Order.shop_id == shop_id)
        .group_by(Payment.order_id)
        .subquery()
    )

    # Common filtering conditions.
    conditions = [
        Order.shop_id == shop_id,
        Customer.shop_id == shop_id,
        Order.created_at >= start_datetime,
        Order.created_at < end_datetime
    ]

    if search and search.strip():

        search = search.strip()

        conditions.append(
            or_(
                Customer.name.icontains(
                    search, autoescape=True
                ),
                Customer.mobile.contains(
                    search, autoescape=True
                ),
                Customer.alternate_mobile.contains(
                    search, autoescape=True
                )
            )
        )

    # Count matching orders before pagination.
    count_query = (
        select(func.count(Order.id))
        .join(Customer, Order.customer_id == Customer.id)
        .where(*conditions)
    )

    result = await db.execute(count_query)

    total = result.scalar_one()

    # Retrieve paginated orders.
    query = (
        select(
            Order.id.label("order_id"),
            Order.customer_id,
            Customer.name.label("customer_name"),
            Customer.mobile.label("customer_mobile"),
            Order.total_amount,
            Order.status.label("order_status"),
            Order.created_at,
            func.coalesce(
                payment_totals.c.amount_paid, 0
            ).label("amount_paid")
        )
        .join(Customer, Order.customer_id == Customer.id)
        .outerjoin(
            payment_totals,
            Order.id == payment_totals.c.order_id
        )
        .where(*conditions)
        .order_by(
            Order.created_at.desc(),
            Order.id.desc()
        )
        .limit(limit)
        .offset(offset)
    )

    result = await db.execute(query)

    rows = result.mappings().all()

    items = []

    for row in rows:

        total_amount = Decimal(
            row["total_amount"]
        ).quantize(Decimal("0.01"))

        amount_paid = Decimal(
            row["amount_paid"]
        ).quantize(Decimal("0.01"))

        amount_due, payment_status = calculate_payment_status(
            order_status=row["order_status"],
            total_amount=total_amount,
            amount_paid=amount_paid
        )

        items.append(
            DashboardOrderResponse(
                order_id=row["order_id"],
                customer_id=row["customer_id"],
                customer_name=row["customer_name"],
                customer_mobile=row["customer_mobile"],
                total_amount=total_amount,
                amount_paid=amount_paid,
                amount_due=amount_due,
                order_status=row["order_status"],
                payment_status=payment_status,
                created_at=row["created_at"]
            )
        )

    return DashboardOrdersResponse(
        items=items,
        total=total,
        limit=limit,
        offset=offset
    )


async def get_dashboard_transactions(
    db: AsyncSession,
    shop_id: UUID,
    start_date: date | None = None,
    end_date: date | None = None,
    search: str | None = None,
    limit: int = 20,
    offset: int = 0
) -> DashboardTransactionsResponse:

    (
        start_date,
        end_date,
        start_datetime,
        end_datetime
    ) = resolve_date_range(start_date, end_date)

    conditions = [
        Order.shop_id == shop_id,
        Customer.shop_id == shop_id,
        Order.status == OrderStatus.COMPLETED,
        Payment.created_at >= start_datetime,
        Payment.created_at < end_datetime
    ]

    # Customer search.
    if search and search.strip():

        search = search.strip()

        conditions.append(
            or_(
                Customer.name.icontains(
                    search, autoescape=True
                ),
                Customer.mobile.contains(
                    search, autoescape=True
                ),
                Customer.alternate_mobile.contains(
                    search, autoescape=True
                )
            )
        )

    # Count matching transactions.
    count_query = (
        select(func.count(Payment.id))
        .join(Order, Payment.order_id == Order.id)
        .join(Customer, Order.customer_id == Customer.id)
        .where(*conditions)
    )

    result = await db.execute(count_query)

    total = result.scalar_one()

    # Retrieve paginated transactions.
    query = (
        select(
            Payment.id.label("payment_id"),
            Payment.order_id,
            Customer.id.label("customer_id"),
            Customer.name.label("customer_name"),
            Customer.mobile.label("customer_mobile"),
            Payment.amount,
            Payment.payment_method,
            Payment.reference,
            Payment.created_at
        )
        .join(Order, Payment.order_id == Order.id)
        .join(Customer, Order.customer_id == Customer.id)
        .where(*conditions)
        .order_by(
            Payment.created_at.desc(),
            Payment.id.desc()
        )
        .limit(limit)
        .offset(offset)
    )

    result = await db.execute(query)

    rows = result.mappings().all()

    items = [
        DashboardTransactionResponse(**row)
        for row in rows
    ]

    return DashboardTransactionsResponse(
        items=items,
        total=total,
        limit=limit,
        offset=offset
    )