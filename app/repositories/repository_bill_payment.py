# app/repositories/repository_bill_payment.py
from typing import Optional
import uuid
from sqlmodel import Session, select
from app.models.rls.m_bill_payment_rls import BillPaymentDB
from app.models.rls.m_bill_payment_allocation_rls import BillPaymentAllocationDB

class BillPaymentRepository:
    def get_all_payments(self, session: Session):
        statement = select(BillPaymentDB)
        return session.exec(statement).all()
    
    def save_payment(self, payment: BillPaymentDB, session: Session, commit: bool = True) -> BillPaymentDB:
        session.add(payment)
        if commit:
            session.commit()
            session.refresh(payment)
        return payment
   
    def get_all_payment_allocations(self, session: Session):
        statement = select(BillPaymentAllocationDB)
        return session.exec(statement).all()

    def get_allocations_by_payment_id(self, payment_id: uuid.UUID, session: Session):
        """Get all allocations for a specific payment"""
        statement = select(BillPaymentAllocationDB).where(
            BillPaymentAllocationDB.source_id == payment_id,
            BillPaymentAllocationDB.source_type == "payment"
        )
        return session.exec(statement).all()
    
    def save_payment_allocation(self, payment_allocation: BillPaymentAllocationDB, session: Session, commit: bool = True) -> BillPaymentAllocationDB:
        session.add(payment_allocation)
        if commit:
            session.commit()
            session.refresh(payment_allocation)
        return payment_allocation

    def get_payment_by_id(self, payment_id: uuid.UUID, session: Session) -> Optional[BillPaymentDB]:
        statement = select(BillPaymentDB).where(BillPaymentDB.id == payment_id)
        return session.exec(statement).first()

    def update_payment(self, payment: BillPaymentDB, session: Session) -> BillPaymentDB:
        session.add(payment)
        session.commit()
        session.refresh(payment)
        return payment


bill_payment_repository = BillPaymentRepository()

