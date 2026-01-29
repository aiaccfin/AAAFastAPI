# app/repositories/gst_repository.py
from typing import Optional
import uuid
from sqlmodel import Session, select
from sqlalchemy.orm import selectinload
from app.models.rls.m_payment_rls import PaymentDB
from app.models.rls.m_payment_allocation_rls import PaymentAllocationDB

class PaymentRepository:
    def get_all_payments(self, session: Session):
        statement = select(PaymentDB)
        return session.exec(statement).all()
    
    def save_payment(self, payment: PaymentDB, session: Session) -> PaymentDB:
        session.add(payment)
        session.commit()
        session.refresh(payment)
        return payment
   
    def get_all_payment_allocations(self, session: Session):
        statement = select(PaymentAllocationDB)
        return session.exec(statement).all()
    
    def save_payment_allocation(self, payment_allocation: PaymentAllocationDB, session: Session) -> PaymentAllocationDB:
        session.add(payment_allocation)
        session.commit()
        session.refresh(payment_allocation)
        return payment_allocation   


    # def get_payment_by_id(self, pmt_id: uuid.UUID, session: Session, ) -> Optional[PaymentDB]:
    #     statement = select(PaymentDB).where(PaymentDB.id == pmt_id)
    #     return session.exec(statement).first()

    def get_allocation_by_id(self, alloc_id: uuid.UUID, session: Session, ) -> Optional[PaymentDB]:
        statement = select(PaymentDB).where(PaymentDB.id == alloc_id)
        return session.exec(statement).first()


    def get_payment_by_id(
        self, pmt_id: uuid.UUID, session: Session
    ) -> Optional[PaymentDB]:

        statement = (
            select(PaymentDB)
            .where(PaymentDB.id == pmt_id)
            .options(
                selectinload(PaymentDB.payment_allocations)
            )
        )

        return session.exec(statement).first()


    def update_Payment(self, Payment: PaymentDB, session: Session, ) -> PaymentDB:
            session.add(Payment)
            session.commit()
            session.refresh(Payment)
            return Payment
        

payment_repository = PaymentRepository()
