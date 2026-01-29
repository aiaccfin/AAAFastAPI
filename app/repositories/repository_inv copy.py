# app/repositories/gst_repository.py
import uuid
from sqlmodel import Session, select
from sqlalchemy.orm import selectinload
from app.models.rls.m_invoice_rls import InvoiceDB
from app.models.rls.m_payment_allocation_rls import PaymentAllocationDB


class InvRepository:
    def get_all(self, session: Session):
        statement = select(InvoiceDB).where(InvoiceDB.is_deleted.isnot(True))
        return session.exec(statement).all()


    def get_all_pagination(self, session: Session, page: int = 1, page_size: int = 20):
        statement = select(InvoiceDB).where(InvoiceDB.is_deleted.isnot(True))
        statement = statement.offset((page - 1) * page_size).limit(page_size)
        return session.exec(statement).all()


    def get_invoice_by_id(self, invoice_id: str | uuid.UUID, session: Session) -> InvoiceDB | None:
        # statement = select(InvoiceDB).where(InvoiceDB.id == invoice_id)
        statement = (
            select(InvoiceDB)
            .where(InvoiceDB.id == invoice_id)
            .options(
                selectinload(InvoiceDB.payment_allocations)
                .selectinload(PaymentAllocationDB.payment)
            )
        )
        return session.exec(statement).first()


    def get_invoice_by_number(self, invoice_number: str, session: Session) -> InvoiceDB | None:
        # Extract sequence number from invoice formats like "INV-1001" or "1001"
        try:
            sequence = int(invoice_number.split('-')[-1])
        except ValueError:
            return None

        statement = (
            select(InvoiceDB)
            .where(InvoiceDB.invoice_sequence == sequence)
            .options(
                selectinload(InvoiceDB.payment_allocations)
                .selectinload(PaymentAllocationDB.payment)
            )
        )

        return session.exec(statement).first()


    def save_invoice(self, invoice: InvoiceDB, session: Session) -> InvoiceDB:
        session.add(invoice)
        session.commit()
        session.refresh(invoice)
        return invoice

    def update_invoice(self, session: Session, invoice: InvoiceDB) -> InvoiceDB:
            session.add(invoice)
            session.commit()
            session.refresh(invoice)
            return invoice
        
        
    def get_by_customer_id(self, session: Session, customer_id: str):
        statement = (
            select(InvoiceDB)
            .where(InvoiceDB.customer_id == customer_id)
            .order_by(InvoiceDB.created_at.desc())
        )
        return session.exec(statement).all()

inv_repository = InvRepository()
