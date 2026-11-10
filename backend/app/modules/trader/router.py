from datetime import date

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.dependencies.db import get_session
from backend.app.dependencies.owner_auth import get_current_owner

from .schema import (
    TraderOrderCreate,
    TraderOrderUpdate,
    TraderOrderResponse,
)

from backend.app.modules.order.models import PaymentStatus

from .service import (
    get_trader_orders,
    create_trader_order,
    update_trader_order,
    delete_trader_order,
)


trader_order_router = APIRouter(
    prefix="/api/traderOrders",
    tags=["Trader Orders"],
)


@trader_order_router.get("/", response_model=list[TraderOrderResponse])
async def read_trader_orders(
    trader_name: str | None = None,
    trader_phone_number: str | None = None,
    start_date: date | None = None,
    end_date: date | None = None,
    payment_status: PaymentStatus | None = None,
    business_name: str | None = None,
    db: AsyncSession = Depends(get_session),
    current_owner=Depends(get_current_owner),
):
    return await get_trader_orders(
        db=db,
        trader_name=trader_name,
        trader_phone_number=trader_phone_number,
        start_date=start_date,
        end_date=end_date,
        payment_status=payment_status,
        business_name=business_name,
    )


@trader_order_router.post("/", response_model=TraderOrderResponse)
async def add_trader_order(
    order_data: TraderOrderCreate,
    db: AsyncSession = Depends(get_session),
    current_owner=Depends(get_current_owner),
):
    return await create_trader_order(
        db=db,
        order_data=order_data,
    )


@trader_order_router.patch(
    "/{order_id}",
    response_model=TraderOrderResponse,
)
async def edit_trader_order(
    order_id: str,
    order_data: TraderOrderUpdate,
    db: AsyncSession = Depends(get_session),
    current_owner=Depends(get_current_owner),
):
    return await update_trader_order(
        db=db,
        order_id=order_id,
        order_data=order_data,
    )


@trader_order_router.delete("/{order_id}")
async def remove_trader_order(
    order_id: str,
    db: AsyncSession = Depends(get_session),
    current_owner=Depends(get_current_owner),
):
    return await delete_trader_order(
        db=db,
        order_id=order_id,
    )