from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import date

from backend.app.dependencies.db import get_session

from backend.app.dependencies.owner_auth import (
    get_current_owner
)

from .models import (
    CustomerOrderStatus,
    PaymentStatus,
)

from .schema import (
    CustomerOrderCreate,
    CustomerOrderUpdate,
    CustomerOrderResponse,
    TraderOrderCreate,
    TraderOrderUpdate,
    TraderOrderResponse,
)

from .service import (
    get_customer_orders,
    create_customer_order,
    update_customer_order,
    delete_customer_order,
    get_trader_orders,
    create_trader_order,
    update_trader_order,
    delete_trader_order,

)

order_router = APIRouter(
    prefix="/Order",
    tags=["Orders"],
)


@order_router.get("/")
async def read_customer_orders(
    phone_number: str | None = Query(
        None, min_length=10, max_length=10
    ),
    customer_id: str | None = None,
    order_id: str | None = None,
    order_status: CustomerOrderStatus | None = None,
    branch_address: str | None = None,
    payment_status: PaymentStatus | None = None,
    db: AsyncSession = Depends(get_session),
    current_owner=Depends(get_current_owner),
):
    return await get_customer_orders(
        db=db,
        current_owner=current_owner,
        phone_number=phone_number,
        customer_id=customer_id,
        order_id=order_id,
        order_status=order_status,
        branch_address=branch_address,
        payment_status=payment_status,
    )


@order_router.post(
    "/",
    response_model=CustomerOrderResponse,
)
async def add_customer_order(
    order_data: CustomerOrderCreate,
    db: AsyncSession = Depends(get_session),
    current_owner=Depends(get_current_owner),
):
    return await create_customer_order(
        db=db,
        current_owner=current_owner,
        order_data=order_data,
    )


@order_router.patch(
    "/{order_id}",
    response_model=CustomerOrderResponse,
)
async def edit_customer_order(
    order_id: str,
    order_data: CustomerOrderUpdate,
    phone_number: str | None = Query(
        None, min_length=10, max_length=10
    ),
    db: AsyncSession = Depends(get_session),
    current_owner=Depends(get_current_owner),
):
    return await update_customer_order(
        db=db,
        current_owner=current_owner,
        order_id=order_id,
        phone_number=phone_number,
        new_status=order_data.order_status,
    )


@order_router.delete("/{order_id}")
async def remove_customer_order(
    order_id: str,
    db: AsyncSession = Depends(get_session),
    current_owner=Depends(get_current_owner),
):
    return await delete_customer_order(
        db=db,
        order_id=order_id,
    )



@order_router.get("/")
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
    if start_date and end_date and start_date > end_date:
        from fastapi import HTTPException
        raise HTTPException(400, "start_date cannot exceed end_date")

    return await get_trader_orders(
        db=db,
        trader_name=trader_name,
        trader_phone_number=trader_phone_number,
        start_date=start_date,
        end_date=end_date,
        payment_status=payment_status,
        business_name=business_name,
    )


@order_router.post(
    "/",
    response_model=TraderOrderResponse,
)
async def add_trader_order(
    order_data: TraderOrderCreate,
    db: AsyncSession = Depends(get_session),
    current_owner=Depends(get_current_owner),
):
    return await create_trader_order(
        db=db,
        order_data=order_data,
    )


@order_router.patch(
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


@order_router.delete("/{order_id}")
async def remove_trader_order(
    order_id: str,
    db: AsyncSession = Depends(get_session),
    current_owner=Depends(get_current_owner),
):
    return await delete_trader_order(
        db=db,
        order_id=order_id,
    )