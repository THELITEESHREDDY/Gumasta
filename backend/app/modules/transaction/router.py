from datetime import date

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.dependencies.db import get_session
from backend.app.dependencies.owner_auth import get_current_owner

from .models import PartyType
from .schema import (
    TransactionCreate,
    TransactionResponse,
)

from .service import (
    get_transactions,
    get_transaction_by_id,
    create_transaction,
)


transaction_router = APIRouter(
    prefix="/transaction",
    tags=["Transactions"],
)


@transaction_router.get(
    "/",
    response_model=list[TransactionResponse],
)
async def read_transactions(
    sender_id: str | None = None,
    receiver_id: str | None = None,
    sender_type: PartyType | None = None,
    receiver_type: PartyType | None = None,
    start_date: date | None = None,
    end_date: date | None = None,
    db: AsyncSession = Depends(get_session),
    current_owner=Depends(get_current_owner),
):
    return await get_transactions(
        db=db,
        sender_id=sender_id,
        receiver_id=receiver_id,
        sender_type=sender_type,
        receiver_type=receiver_type,
        start_date=start_date,
        end_date=end_date,
    )


@transaction_router.get(
    "/{transaction_id}",
    response_model=TransactionResponse,
)
async def read_transaction(
    transaction_id: str,
    db: AsyncSession = Depends(get_session),
    current_owner=Depends(get_current_owner),
):
    return await get_transaction_by_id(
        db=db,
        transaction_id=transaction_id,
    )


@transaction_router.post(
    "/",
    response_model=TransactionResponse,
)
async def add_transaction(
    transaction_data: TransactionCreate,
    db: AsyncSession = Depends(get_session),
    current_owner=Depends(get_current_owner),
):
    return await create_transaction(
        db=db,
        transaction_data=transaction_data,
    )