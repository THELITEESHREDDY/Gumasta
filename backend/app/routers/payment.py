from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.dependencies import get_owned_shop
from app.models.shop import Shop

from app.schemas.payment import (
    PaymentCreate,
    PaymentResponse,
    PaymentSummary
)

from app.services.payment_service import (
    create_payment,
    get_payments,
    get_payment_summary,
    InvalidPaymentError,
    OverpaymentError
)

from app.services.order_service import OrderNotFoundError


router = APIRouter(
    prefix="/shops/{shop_id}/orders/{order_id}",
    tags=["Payments"]
)

@router.post(
    "/payments",
    response_model=PaymentResponse,
    status_code=status.HTTP_201_CREATED
)
async def create(
    order_id: UUID,
    data: PaymentCreate,
    shop: Shop = Depends(get_owned_shop),
    db: AsyncSession = Depends(get_db)
):
    try:
        return await create_payment(
            db=db,
            shop_id=shop.id,
            order_id=order_id,
            data=data
        )

    except OrderNotFoundError:
        raise HTTPException(
            status_code=404,
            detail="Order not found"
        )

    except InvalidPaymentError as exc:
        raise HTTPException(
            status_code=409,
            detail=str(exc)
        )

    except OverpaymentError as exc:
        raise HTTPException(
            status_code=409,
            detail=str(exc)
        )

@router.get(
    "/payments",
    response_model=list[PaymentResponse]
)
async def list_payments(
    order_id: UUID,
    shop: Shop = Depends(get_owned_shop),
    db: AsyncSession = Depends(get_db)
):
    try:
        return await get_payments(
            db=db,
            shop_id=shop.id,
            order_id=order_id
        )

    except OrderNotFoundError:
        raise HTTPException(
            status_code=404,
            detail="Order not found"
        )


@router.get(
    "/payment-summary",
    response_model=PaymentSummary
)
async def payment_summary(
    order_id: UUID,
    shop: Shop = Depends(get_owned_shop),
    db: AsyncSession = Depends(get_db)
):
    try:
        return await get_payment_summary(
            db=db,
            shop_id=shop.id,
            order_id=order_id
        )

    except OrderNotFoundError:
        raise HTTPException(
            status_code=404,
            detail="Order not found"
        )