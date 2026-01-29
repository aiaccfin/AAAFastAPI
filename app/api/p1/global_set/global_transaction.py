from uuid import UUID
from typing import List

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.db_async import get_db
from app.services.ser_transaction import TransactionService
from app.schemas.sch_transaction import TransactionCreate,TransactionUpdate,TransactionRead

router = APIRouter()
TENANT_ID = "550e8400-e29b-41d4-a716-446655440000"


def get_service(
    db: AsyncSession = Depends(get_db),
) -> TransactionService:
    return TransactionService(db)


@router.post(
    "",
    response_model=TransactionRead,
    status_code=status.HTTP_201_CREATED,
)
async def create_transaction(
    payload: TransactionCreate,
    service: TransactionService = Depends(get_service),
):
    return await service.create(payload)


@router.get(
    "",
    response_model=List[TransactionRead],
)
async def list_transactions(
    service: TransactionService = Depends(get_service),
):
    return await service.list()


@router.get(
    "/{transaction_id}",
    response_model=TransactionRead,
)
async def get_transaction(
    transaction_id: UUID,
    service: TransactionService = Depends(get_service),
):
    return await service.get(transaction_id)


@router.put(
    "/{transaction_id}",
    response_model=TransactionRead,
)
async def update_transaction(
    transaction_id: UUID,
    payload: TransactionUpdate,
    service: TransactionService = Depends(get_service),
):
    return await service.update(transaction_id, payload)


@router.delete(
    "/{transaction_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_transaction(
    transaction_id: UUID,
    service: TransactionService = Depends(get_service),
):
    await service.soft_delete(transaction_id)
