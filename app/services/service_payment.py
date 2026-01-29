# app/services/service_salestax.py - UPDATED
from typing import Optional
import uuid
from sqlmodel import Session, select
from app.repositories.repository_payment import payment_repository
from app.repositories.repository_inv import inv_repository

from app.models.rls.m_payment_rls import PaymentDB, PaymentCreate, PaymentRead
from app.models.rls.m_payment_allocation_rls import PaymentAllocationDB, PaymentAllocationCreate, PaymentAllocationRead
from app.models.rls.m_invoice_rls import InvoiceDB

class PaymentService:

    def list_payments(self, session: Session):
        return payment_repository.get_all_payments(session)

    def create_payment(self, data: PaymentCreate, tenant_id: str, session: Session) -> PaymentDB:
        new_payment = PaymentDB(**data.dict(), tenant_id=tenant_id)
        return payment_repository.save_payment(new_payment, session)

    def list_payment_allocations(self, session: Session):
        return payment_repository.get_all_payment_allocations(session)
    
    def create_payment_allocation(self, data: PaymentAllocationCreate, tenant_id: str, session: Session) -> PaymentAllocationDB:
        # 1. Create allocation
        new_payment_allocation = PaymentAllocationDB(**data.dict(), tenant_id=tenant_id)
        return payment_repository.save_payment_allocation(new_payment_allocation, session)


    def get_payment_by_id(self, pmt_id: uuid.UUID, session: Session) -> Optional[PaymentDB]:
        return payment_repository.get_payment_by_id(pmt_id, session)

    def get_allocation_by_id(self, alloc_id: uuid.UUID, session: Session) -> Optional[PaymentDB]:
        return payment_repository.get_allocation_by_id(alloc_id, session)


    def update_payment(self, pmt_id: uuid.UUID, update_obj: dict, session: Session):
        payment = payment_repository.get_payment_by_id(pmt_id=pmt_id, session=session)
        if not payment:
            return None

        update_data = update_obj.dict(exclude_unset=True)

        for key, value in update_data.items():
            setattr(payment, key, value)

        session.add(payment)
        session.commit()
        session.refresh(payment)
        return payment


    def update_allocation(self, alloc_id: uuid.UUID, update_obj: dict, session: Session):
        alloc = payment_repository.get_allocation_by_id(alloc_id=alloc_id, session=session)
        if not alloc:return None

        update_data = update_obj.dict(exclude_unset=True)

        for key, value in update_data.items():
            setattr(alloc, key, value)

        session.add(alloc)
        session.commit()
        session.refresh(alloc)
        return alloc

# Service instance
payment_service = PaymentService()