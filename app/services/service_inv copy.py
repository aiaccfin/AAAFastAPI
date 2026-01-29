# app/services/service_salestax.py - UPDATED
from typing import List, Optional
from requests import session
from sqlmodel import Session, select
from datetime import datetime
import uuid
from app.repositories.repository_inv import inv_repository
from app.models.rls.m_invoice_rls import InvoiceDB, InvoiceCreate, InvoiceUpdate
from app.models.rls.m_journal_entry_rls import JournalEntry, JournalEntryCreate
from sqlmodel import Session, text, select
from sqlalchemy import func
from app.models.rls.m_invoice_rls import InvoiceDB


class InvService:
    
    def replace_invoice(self, invoice_id: uuid.UUID, data: InvoiceUpdate, session: Session) -> Optional[InvoiceDB]:
        invoice = inv_repository.get_invoice_by_id(invoice_id, session)
        if not invoice:
            return None

        # Full replace: overwrite all updatable fields
        update_data = data.dict(exclude_unset=False)

        for field, value in update_data.items():
            setattr(invoice, field, value)

        inv_repository.save_invoice(invoice, session)
        return invoice



    def get_next_invoice_number_for_me(self, db: Session, tenant_id: uuid.UUID) -> int:
        stmt = text("SELECT next_invoice_number(:tenant_id)")
        result = db.exec(stmt, params={"tenant_id": str(tenant_id)})
        db.commit()
        return result.scalar_one()

    def list_inv(self, session: Session):
        return inv_repository.get_all(session)


    def list_inv_pagination(self, session: Session, page: int = 1, page_size: int = 20):
        return inv_repository.get_all_pagination(session=session, page=page, page_size=page_size)


    def get_invoice_by_id(self, invoice_id: uuid.UUID, session: Session) -> Optional[InvoiceDB]:
        return inv_repository.get_invoice_by_id(invoice_id, session)

    def get_invoice_by_number(self, invoice_number: str, session: Session) -> Optional[InvoiceDB]:
        return inv_repository.get_invoice_by_number(invoice_number, session)

    def create_invoice(self, data: InvoiceCreate, tenant_id: str, session: Session) -> InvoiceDB:
        new_invoice = InvoiceDB(**data.dict(), tenant_id=tenant_id)
        inv_repository.save_invoice(new_invoice, session)
        return new_invoice

    def update_invoice(self, invoice_id: uuid.UUID, data: InvoiceUpdate, session: Session):
        invoice = inv_repository.get_invoice_by_id(invoice_id, session)
        if not invoice:            return None

        update_data = data.dict(exclude_unset=True)

        for key, value in update_data.items():
            setattr(invoice, key, value)

        updated_invoice = inv_repository.update_invoice(session, invoice)
        return updated_invoice

    def get_invoices_by_customer(self, session: Session, customer_id: str):
            return inv_repository.get_by_customer_id(session, customer_id)













    def query_inv(
        self,
        session: Session,
        skip: int = 0,
        limit: int = 100,
        status: Optional[str] = None,
        payment_status: Optional[str] = None,
        customer_id: Optional[str] = None
    ) -> List[InvoiceDB]:
        statement = select(InvoiceDB).where(
            InvoiceDB.tenant_id == "550e8400-e29b-41d4-a716-446655440000")

        if status:
            statement = statement.where(InvoiceDB.status == status)
        if payment_status:
            statement = statement.where(
                InvoiceDB.payment_status == payment_status)
        if customer_id:
            statement = statement.where(InvoiceDB.customer_id == customer_id)

        statement = statement.offset(skip).limit(
            limit).order_by(InvoiceDB.created_at.desc())
        return session.exec(statement).all()


    def _create_journal_entry_for_invoice(self, invoice: InvoiceDB, session: Session) -> JournalEntry:
        """Create a journal entry for the invoice using YOUR model structure"""

        # Calculate total debit/credit (should be equal for balanced entry)
        total_amount = invoice.total_amount

        # Create journal entry data that matches YOUR model
        journal_data = JournalEntryCreate(
            description=f"Invoice {invoice.full_invoice_number} for {invoice.customer_name}",
            transaction_date=invoice.issue_date,
            account_id="accounts_receivable",  # Required by your model

            # Amount fields - for invoice: debit accounts receivable
            debit_amount=total_amount,
            credit_amount=0,
            balance=total_amount,

            # Link to invoice
            reference_invoice_id=invoice.id,

            # Status
            status="posted",

            # Additional notes
            notes={
                "invoice_number": invoice.full_invoice_number,
                "customer_name": invoice.customer_name,
                "line_items": invoice.line_items,
                "tax_amount": invoice.tax_amount
            }
        )

        # Create journal entry WITH TENANT_ID
        journal_entry = JournalEntry(
            **journal_data.dict(),
            tenant_id=invoice.tenant_id,  # 🔥 CRITICAL: Add tenant_id here
            journal_entry_prefix="JE"  # Fixed prefix without trailing dash
        )

        session.add(journal_entry)
        session.commit()
        session.refresh(journal_entry)

        return journal_entry

    # Simplified payment method for YOUR model

    def update_invoice_payment(self, invoice_id: uuid.UUID, payment_amount: float, session: Session) -> InvoiceDB:
        """Update invoice payment and create payment journal entry"""
        # Get invoice
        statement = select(InvoiceDB).where(InvoiceDB.id == invoice_id)
        invoice = session.exec(statement).first()

        if not invoice:
            raise ValueError("Invoice not found")

        # Update invoice payment
        invoice.amount_paid += payment_amount
        invoice.balance_due = invoice.total_amount - invoice.amount_paid

        # Update payment status
        if invoice.amount_paid >= invoice.total_amount:
            invoice.payment_status = "paid"
        elif invoice.amount_paid > 0:
            invoice.payment_status = "partial"

        session.add(invoice)
        session.commit()
        session.refresh(invoice)

        # Create payment journal entry if payment was made
        if payment_amount > 0:
            self._create_payment_journal_entry(
                invoice, payment_amount, session)

        return invoice

    def _create_payment_journal_entry(self, invoice: InvoiceDB, payment_amount: float, session: Session):
        """Create journal entry for invoice payment using YOUR model"""
        journal_data = JournalEntryCreate(
            description=f"Payment received for invoice {invoice.full_invoice_number}",
            transaction_date=datetime.utcnow(),
            account_id="cash",  # Cash account increases (debit)

            # For payment: debit cash, credit accounts receivable
            debit_amount=payment_amount,  # Cash increases
            credit_amount=0,
            balance=payment_amount,

            # Link to invoice
            reference_invoice_id=invoice.id,

            status="posted",
            notes={
                "payment_for_invoice": invoice.full_invoice_number,
                "customer_name": invoice.customer_name
            },
            tenant_id=invoice.tenant_id
        )

        journal_entry = JournalEntry(**journal_data.dict())
        session.add(journal_entry)
        session.commit()


# Service instance
inv_service = InvService()
