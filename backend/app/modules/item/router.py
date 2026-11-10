from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.dependencies.db import get_session
from backend.app.dependencies.owner_auth import get_current_owner

from .schema import (
    ItemCreate,
    ItemUpdate,
    ItemResponse,
)

from .service import (
    get_items,
    create_item,
    update_item,
    delete_item,
)


item_router = APIRouter(
    prefix="/api/item",
    tags=["Items"],
)


# Public: List or search items
@item_router.get("/")
async def read_items(
    item_name: str | None = None,
    item_id: str | None = None,
    db: AsyncSession = Depends(get_session),
):
    return await get_items(
        db=db,
        item_name=item_name,
        item_id=item_id,
    )


# Owner only: Create item
@item_router.post("/", response_model=ItemResponse)
async def add_item(
    item_data: ItemCreate,
    db: AsyncSession = Depends(get_session),
    current_owner=Depends(get_current_owner),
):
    return await create_item(
        db=db,
        item_data=item_data,
    )


# Owner only: Update item
@item_router.patch("/", response_model=ItemResponse)
async def edit_item(
    item_id: str = Query(...),
    item_data: ItemUpdate = ...,
    db: AsyncSession = Depends(get_session),
    current_owner=Depends(get_current_owner),
):
    return await update_item(
        db=db,
        item_id=item_id,
        item_data=item_data,
    )


# Owner only: Delete item
@item_router.delete("/")
async def remove_item(
    item_id: str = Query(...),
    db: AsyncSession = Depends(get_session),
    current_owner=Depends(get_current_owner),
):
    return await delete_item(
        db=db,
        item_id=item_id,
    )