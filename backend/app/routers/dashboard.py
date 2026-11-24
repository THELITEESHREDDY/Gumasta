from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.dependencies import get_owned_shop
from app.models.shop import Shop

from app.schemas.dashboard import (
    DashboardSummary,
    DashboardOrdersResponse,
    DashboardTransactionsResponse
)

from app.services.dashboard_service import (
    get_dashboard_summary,
    get_dashboard_orders,
    get_dashboard_transactions,
    InvalidDateRangeError
)


router = APIRouter(
    prefix="/shops/{shop_id}/dashboard",
    tags=["Dashboard"]
)


@router.get("/summary", response_model=DashboardSummary)
async def dashboard_summary(
    start_date: date | None = None,
    end_date: date | None = None,
    shop: Shop = Depends(get_owned_shop),
    db: AsyncSession = Depends(get_db)
):
    try:
        return await get_dashboard_summary(
            db=db,
            shop_id=shop.id,
            start_date=start_date,
            end_date=end_date
        )

    except InvalidDateRangeError as exc:
        raise HTTPException(
            status_code=422,
            detail=str(exc)
        )


@router.get("/orders", response_model=DashboardOrdersResponse)
async def dashboard_orders(
    start_date: date | None = None,
    end_date: date | None = None,
    search: str | None = Query(default=None, max_length=100),
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    shop: Shop = Depends(get_owned_shop),
    db: AsyncSession = Depends(get_db)
):
    try:
        return await get_dashboard_orders(
            db=db,
            shop_id=shop.id,
            start_date=start_date,
            end_date=end_date,
            search=search,
            limit=limit,
            offset=offset
        )

    except InvalidDateRangeError as exc:
        raise HTTPException(
            status_code=422,
            detail=str(exc)
        )

@router.get(
    "/transactions",
    response_model=DashboardTransactionsResponse
)
async def dashboard_transactions(
    start_date: date | None = None,
    end_date: date | None = None,
    search: str | None = Query(default=None, max_length=100),
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    shop: Shop = Depends(get_owned_shop),
    db: AsyncSession = Depends(get_db)
):
    try:
        return await get_dashboard_transactions(
            db=db,
            shop_id=shop.id,
            start_date=start_date,
            end_date=end_date,
            search=search,
            limit=limit,
            offset=offset
        )

    except InvalidDateRangeError as exc:
        raise HTTPException(
            status_code=422,
            detail=str(exc)
        )


