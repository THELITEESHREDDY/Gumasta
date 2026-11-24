from uuid import UUID
from datetime import date

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.dependencies import get_owned_shop
from app.models.shop import Shop
from app.models.order import OrderStatus

from app.schemas.order import (
    OrderCreate,
    OrderResponse,
    OrderDetailResponse
)

from app.services.order_service import (
    create_order,
    get_orders,
    get_order,
    cancel_order,
    OrderNotFoundError,
    InvalidOrderError,
    InsufficientStockError,
    OrderCancellationError
)


router = APIRouter(
    prefix="/shops/{shop_id}/orders",
    tags=["Orders"]
)


@router.post(
    "",
    response_model=OrderDetailResponse,
    status_code=status.HTTP_201_CREATED
)
async def create(
    data: OrderCreate,
    shop: Shop = Depends(get_owned_shop),
    db: AsyncSession = Depends(get_db)
):
    try:
        return await create_order(
            db=db,
            shop_id=shop.id,
            data=data
        )

    except InvalidOrderError as exc:
        raise HTTPException(
            status_code=422,
            detail=str(exc)
        )

    except InsufficientStockError as exc:
        raise HTTPException(
            status_code=409,
            detail=str(exc)
        )


@router.get(
    "",
    response_model=list[OrderResponse]
)
async def list_orders(
    start_date: date | None = None,
    end_date: date | None = None,
    customer_id: UUID | None = None,
    status: OrderStatus | None = None,
    shop: Shop = Depends(get_owned_shop),
    db: AsyncSession = Depends(get_db)
):
    try:
        return await get_orders(
            db=db,
            shop_id=shop.id,
            start_date=start_date,
            end_date=end_date,
            customer_id=customer_id,
            status=status
        )

    except InvalidOrderError as exc:
        raise HTTPException(
            status_code=422,
            detail=str(exc)
        )

@router.get(
    "/{order_id}",
    response_model=OrderDetailResponse
)
async def retrieve(
    order_id: UUID,
    shop: Shop = Depends(get_owned_shop),
    db: AsyncSession = Depends(get_db)
):
    try:
        return await get_order(
            db=db,
            shop_id=shop.id,
            order_id=order_id
        )

    except OrderNotFoundError:
        raise HTTPException(
            status_code=404,
            detail="Order not found"
        )


@router.post(
    "/{order_id}/cancel",
    response_model=OrderDetailResponse
)
async def cancel(
    order_id: UUID,
    shop: Shop = Depends(get_owned_shop),
    db: AsyncSession = Depends(get_db)
):
    try:
        return await cancel_order(
            db=db,
            shop_id=shop.id,
            order_id=order_id
        )

    except OrderNotFoundError:
        raise HTTPException(
            status_code=404,
            detail="Order not found"
        )

    except OrderCancellationError as exc:
        raise HTTPException(
            status_code=409,
            detail=str(exc)
        )