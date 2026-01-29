# app/repositories/gst_repository.py
from typing import Optional
import uuid
from sqlmodel import Session, select
from sqlalchemy.orm import selectinload
from app.models.rls.m_payment_allocation_rls import PaymentAllocationDB

class PaymentAllocationRepository:
    def get_all_payment_allocations(self, session: Session):
        statement = select(PaymentAllocationDB)
        return session.exec(statement).all()
    
    def save_payment_allocation(self, payment_allocation: PaymentAllocationDB, session: Session) -> PaymentAllocationDB:
        session.add(payment_allocation)
        session.commit()
        session.refresh(payment_allocation)
        return payment_allocation   


    def get_allocation_by_id(self, alloc_id: uuid.UUID, session: Session, ) -> Optional[PaymentAllocationDB]:
        statement = select(PaymentAllocationDB).where(PaymentAllocationDB.id == alloc_id)
        return session.exec(statement).first()


    def update_allocation(self, Allocation: PaymentAllocationDB, session: Session, ) -> PaymentAllocationDB:
            session.add(Allocation)
            session.commit()
            session.refresh(Allocation)
            return Allocation
        

payment_allocation_repository = PaymentAllocationRepository()
