# app/services/service_salestax.py - UPDATED
from typing import Optional
import uuid
from sqlmodel import Session, select

from app.repositories.repository_payment_allocation import payment_allocation_repository
from app.models.rls.m_payment_allocation_rls import PaymentAllocationDB, PaymentAllocationCreate, PaymentAllocationRead

class PaymentAllocationService:

    def list_payment_allocations(self, session: Session):
        return payment_allocation_repository.get_all_payment_allocations(session)
    
    def create_payment_allocation(self, data: PaymentAllocationCreate, tenant_id: str, session: Session) -> PaymentAllocationDB:
        # 1. Create allocation
        new_payment_allocation = PaymentAllocationDB(**data.dict(), tenant_id=tenant_id)
        return payment_allocation_repository.save_payment_allocation(new_payment_allocation, session)

    def get_allocation_by_id(self, alloc_id: uuid.UUID, session: Session) -> Optional[PaymentAllocationDB]:
        return payment_allocation_repository.get_allocation_by_id(alloc_id, session)


    def update_allocation(self, alloc_id: uuid.UUID, update_obj: dict, session: Session):
        alloc = payment_allocation_repository.get_allocation_by_id(alloc_id=alloc_id, session=session)
        if not alloc:return None

        update_data = update_obj.dict(exclude_unset=True)

        for key, value in update_data.items():
            setattr(alloc, key, value)

        session.add(alloc)
        session.commit()
        session.refresh(alloc)
        return alloc

# Service instance
payment_allocation_service = PaymentAllocationService()