from uuid import UUID
from typing import List

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.repo.repo_transaction import TransactionRepository
from app.db.models.mo_transaction import Transaction


class TransactionService:
    def __init__(self, db: AsyncSession):
        self.repo = TransactionRepository(db)

    async def create(self, payload) -> Transaction:
        return await self.repo.create(payload.model_dump())

    async def list(self) -> List[Transaction]:
        return await self.repo.list()

    async def get(self, tx_id: UUID) -> Transaction:
        tx = await self.repo.get_by_id(tx_id)
        if not tx:
            raise HTTPException(status_code=404, detail="Transaction not found")
        return tx

    async def update(self, tx_id: UUID, payload) -> Transaction:
        tx = await self.repo.update(tx_id, payload.model_dump(exclude_unset=True))
        if not tx:
            raise HTTPException(status_code=404, detail="Transaction not found")
        return tx

    async def soft_delete(self, tx_id: UUID) -> None:
        ok = await self.repo.soft_delete(tx_id)
        if not ok:
            raise HTTPException(status_code=404, detail="Transaction not found")
