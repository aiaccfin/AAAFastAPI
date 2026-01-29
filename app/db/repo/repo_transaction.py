from uuid import UUID
from datetime import datetime
from typing import List, Optional

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.mo_transaction import Transaction


class TransactionRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, data: dict) -> Transaction:
        tx = Transaction(**data)
        self.db.add(tx)
        await self.db.commit()
        await self.db.refresh(tx)
        return tx

    async def get_by_id(self, tx_id: UUID) -> Optional[Transaction]:
        stmt = select(Transaction).where(
            Transaction.id == tx_id,
            Transaction.is_deleted.is_(False),
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def list(self) -> List[Transaction]:
        stmt = select(Transaction).where(Transaction.is_deleted.is_(False))
        result = await self.db.execute(stmt)
        return result.scalars().all()

    async def update(self, tx_id: UUID, data: dict) -> Optional[Transaction]:
        stmt = (
            update(Transaction)
            .where(Transaction.id == tx_id, Transaction.is_deleted.is_(False))
            .values(**data, updated_at=datetime.utcnow())
            .returning(Transaction)
        )
        result = await self.db.execute(stmt)
        await self.db.commit()
        return result.scalar_one_or_none()

    async def soft_delete(self, tx_id: UUID) -> bool:
        stmt = (
            update(Transaction)
            .where(Transaction.id == tx_id, Transaction.is_deleted.is_(False))
            .values(is_deleted=True, updated_at=datetime.utcnow())
        )
        result = await self.db.execute(stmt)
        await self.db.commit()
        return result.rowcount > 0
