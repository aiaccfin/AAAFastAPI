# app/repositories/gst_repository.py
from datetime import datetime
from typing import Optional
import uuid
from sqlmodel import Session, func, select
from sqlalchemy.orm import selectinload
from app.models.rls.m_invoice_rls import InvoiceDB
from app.models.rls.m_payment_allocation_rls import PaymentAllocationDB
from app.models.rls.m_payment_rls import PaymentDB


class InvRepository:
    # def get_all(self, inv_rec, session: Session):
    #     statement = select(InvoiceDB).where(InvoiceDB.is_deleted.isnot(True))
    #     return session.exec(statement).all()

    def get_all_old(self, inv_rec: str | None, session: Session):
        statement = (
            select(InvoiceDB)
            .where(InvoiceDB.is_deleted.isnot(True))
        )

        if inv_rec:
            statement = statement.where(InvoiceDB.inv_rec == inv_rec)

        return session.exec(statement).all()


    def get_all(
        self,
        session: Session,
        page: int,
        page_size: int,
        status: Optional[str] = None,
        payment_status: Optional[str] = None,
        issue_date_start: Optional[datetime] = None,
        issue_date_end: Optional[datetime] = None,
        doc_type: Optional[str] = None,
    ):
        # base
        base_stmt = select(InvoiceDB).where(InvoiceDB.is_deleted.isnot(True))

        # status filter
        if status:
            base_stmt = base_stmt.where(InvoiceDB.status == status)

        if doc_type:
            base_stmt = base_stmt.where(InvoiceDB.inv_rec == doc_type)

        # payment_status filter
        if payment_status:
            base_stmt = base_stmt.where(InvoiceDB.payment_status == payment_status)

        # date filters
        if issue_date_start:
            base_stmt = base_stmt.where(InvoiceDB.issue_date >= issue_date_start)

        if issue_date_end:
            base_stmt = base_stmt.where(InvoiceDB.issue_date <= issue_date_end)

        # count total
        count_stmt = select(func.count()).select_from(base_stmt.subquery())
        total = session.exec(count_stmt).one()

        # pagination
        stmt = base_stmt.offset((page - 1) * page_size).limit(page_size)
        items = session.exec(stmt).all()

        return items, total




    def get_all_pagination_bak(
        self,
        session: Session,
        page: int,
        page_size: int,
        status: Optional[str] = None,
        payment_status: Optional[str] = None,
    ):
        base_stmt = select(InvoiceDB).where(InvoiceDB.is_deleted.isnot(True))

        # Apply filters
        if status:
            base_stmt = base_stmt.where(InvoiceDB.status == status)
        if payment_status:
            base_stmt = base_stmt.where(InvoiceDB.payment_status == payment_status)

        # ---- 1) Count total matching rows ----
        count_stmt = select(func.count()).select_from(
            base_stmt.subquery()
        )
        total = session.exec(count_stmt).one()

        # ---- 2) Apply pagination ----
        stmt = base_stmt.offset((page - 1) * page_size).limit(page_size)
        items = session.exec(stmt).all()

        return items, total


    # def get_all_pagination(
    #     self,
    #     session: Session,
    #     page: int,
    #     page_size: int,
    #     status: Optional[str] = None,
    #     payment_status: Optional[str] = None,
    # ):
    #     stmt = select(InvoiceDB).where(InvoiceDB.is_deleted.isnot(True))

    #     # apply optional filters
    #     if status:
    #         stmt = stmt.where(InvoiceDB.status == status)

    #     if payment_status:
    #         stmt = stmt.where(InvoiceDB.payment_status == payment_status)

    #     # pagination
    #     stmt = stmt.offset((page - 1) * page_size).limit(page_size)

    #     return session.exec(stmt).all()

    # def get_all_pagination(self, session: Session, page: int = 1, page_size: int = 20):
    #     statement = select(InvoiceDB).where(InvoiceDB.is_deleted.isnot(True))
    #     statement = statement.offset((page - 1) * page_size).limit(page_size)
    #     return session.exec(statement).all()


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
        if invoice.inv_rec in ["credits", "CREDIT_NOTE"]:
            payment_entry = PaymentDB(
                amount=invoice.total_amount,
                payment_date = invoice.issue_date,
                payment_type = invoice.inv_rec,
                payment_source = "Credit Note",
                tenant_id=invoice.tenant_id
            )
            session.add(payment_entry)
           
        
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
