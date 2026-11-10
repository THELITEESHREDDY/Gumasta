from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.dependencies.db  import get_session
from backend.app.dependencies.owner_auth import get_current_owner
from .schemas import (
    DashboardFilters,
    SalesDashboardResponse,
)
from .service import get_sales_dashboard
from backend.app.modules.owner.models import Owner


dashboardrouter = APIRouter(
    prefix="/dashboard",
    tags=["Dashboard"],
)


@dashboardrouter.get("/sales/", response_model=SalesDashboardResponse)
async def sales_dashboard(
    filters: DashboardFilters = Depends(),
    db: AsyncSession = Depends(get_session),
    current_owner: Owner = Depends(get_current_owner),
):
    return await get_sales_dashboard(
        db=db,
        owner_id=current_owner.id,
        filters=filters,
    )