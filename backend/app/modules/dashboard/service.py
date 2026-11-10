from decimal import Decimal

from fastapi import HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.modules.shop.models import Shop
from backend.app.modules.order.models import CustomerOrderItem,CustomerOrderStatus,CustomerOrder,Order


from .schemas import (
    DashboardFilters,
    SalesDashboardResponse,
    SalesSummary,
    DailySales,
    ItemSales,
)


ZERO = Decimal("0.00")


async def validate_shop_access(
    db: AsyncSession,
    owner_id: str,
    shop_id: str | None,
) -> None:
    if shop_id is None:
        return

    stmt = select(Shop.id).where(
        Shop.id == shop_id,
        Shop.owner_id == owner_id,
    )

    result = await db.execute(stmt)

    if result.scalar_one_or_none() is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Shop not found",
        )


def apply_sales_filters(
    stmt,
    owner_id: str,
    filters: DashboardFilters,
):
    stmt = (
        stmt
        .join(Order, Order.id == CustomerOrder.order_id)
        .join(Shop, Shop.id == CustomerOrder.shop_id)
        .where(
            Shop.owner_id == owner_id,
            CustomerOrder.order_status != CustomerOrderStatus.CANCELLED,
        )
    )

    if filters.start_date:
        stmt = stmt.where(Order.date >= filters.start_date)

    if filters.end_date:
        stmt = stmt.where(Order.date <= filters.end_date)

    if filters.shop_id:
        stmt = stmt.where(CustomerOrder.shop_id == filters.shop_id)

    # EXISTS avoids multiplying order totals when an order has
    # multiple matching item rows.
    if filters.item_name:
        matching_item = (
            select(CustomerOrderItem.id)
            .where(
                CustomerOrderItem.order_id == CustomerOrder.order_id,
                CustomerOrderItem.item_name.ilike(
                    f"%{filters.item_name}%"
                ),
            )
            .exists()
        )
        stmt = stmt.where(matching_item)

    return stmt


async def get_sales_summary(
    db: AsyncSession,
    owner_id: str,
    filters: DashboardFilters,
) -> SalesSummary:
    stmt = select(
        func.count(Order.id).label("total_orders"),
        func.coalesce(
            func.sum(Order.bill_amount), ZERO
        ).label("total_sales"),
    ).select_from(CustomerOrder)

    stmt = apply_sales_filters(stmt, owner_id, filters)

    result = await db.execute(stmt)
    row = result.one()

    total_orders = row.total_orders
    total_sales = row.total_sales or ZERO

    average = (
        total_sales / total_orders
        if total_orders
        else ZERO
    )

    return SalesSummary(
        total_sales=total_sales,
        total_orders=total_orders,
        average_order_value=average,
    )


async def get_daily_sales(
    db: AsyncSession,
    owner_id: str,
    filters: DashboardFilters,
) -> list[DailySales]:
    stmt = select(
        Order.date.label("date"),
        func.coalesce(
            func.sum(Order.bill_amount), ZERO
        ).label("sales"),
        func.count(Order.id).label("orders"),
    ).select_from(CustomerOrder)

    stmt = apply_sales_filters(stmt, owner_id, filters)

    stmt = (
        stmt
        .group_by(Order.date)
        .order_by(Order.date)
    )

    result = await db.execute(stmt)

    return [
        DailySales(
            date=row.date,
            sales=row.sales or ZERO,
            orders=row.orders,
        )
        for row in result.all()
    ]


async def get_top_items(
    db: AsyncSession,
    owner_id: str,
    filters: DashboardFilters,
    limit: int = 10,
) -> list[ItemSales]:
    stmt = select(
        CustomerOrderItem.item_name,
        func.coalesce(
            func.sum(CustomerOrderItem.quantity), 0
        ).label("quantity_sold"),
        func.coalesce(
            func.sum(CustomerOrderItem.line_total), ZERO
        ).label("revenue"),
        func.coalesce(
            func.sum(
                CustomerOrderItem.quantity
                * (
                    CustomerOrderItem.unit_selling_price
                    - CustomerOrderItem.unit_cost_price
                )
            ),
            ZERO,
        ).label("gross_profit"),
    ).select_from(CustomerOrderItem)

    stmt = (
        stmt
        .join(
            CustomerOrder,
            CustomerOrder.order_id == CustomerOrderItem.order_id,
        )
    )

    stmt = apply_sales_filters(stmt, owner_id, filters)

    stmt = (
        stmt
        .group_by(CustomerOrderItem.item_name)
        .order_by(func.sum(CustomerOrderItem.line_total).desc())
        .limit(limit)
    )

    result = await db.execute(stmt)

    return [
        ItemSales(
            item_name=row.item_name,
            quantity_sold=row.quantity_sold,
            revenue=row.revenue or ZERO,
            gross_profit=row.gross_profit or ZERO,
        )
        for row in result.all()
    ]


async def get_sales_dashboard(
    db: AsyncSession,
    owner_id: str,
    filters: DashboardFilters,
) -> SalesDashboardResponse:
    await validate_shop_access(
        db=db,
        owner_id=owner_id,
        shop_id=filters.shop_id,
    )

    summary = await get_sales_summary(db, owner_id, filters)
    daily_sales = await get_daily_sales(db, owner_id, filters)
    top_items = await get_top_items(db, owner_id, filters)

    return SalesDashboardResponse(
        filters=filters,
        summary=summary,
        daily_sales=daily_sales,
        top_items=top_items,
    )
