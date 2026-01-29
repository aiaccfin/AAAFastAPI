# app/services/helpers/invoice_helper.py
from sqlmodel import Session
from app.repositories.repository_inv import inv_repository
from app.models.rls.m_invoice_rls import InvoiceDB


def update_invoice_balance(invoice_id: str,    delta_amount: float,    session: Session,    prevent_negative: bool = True) -> InvoiceDB:
    """
    Update invoice.balance_due by delta_amount.

    - delta_amount < 0 : deduct (payment allocation)
    - delta_amount > 0 : increase (refund, adjustment)

    This function DOES NOT commit, so you can wrap multiple operations in a transaction.
    """
    invoice: InvoiceDB = inv_repository.get_invoice_by_id(invoice_id, session)
    if not invoice:
        raise Exception(f"Invoice {invoice_id} not found")

    invoice.balance_due += delta_amount

    if prevent_negative and invoice.balance_due < 0:
        invoice.balance_due = 0

    session.add(invoice)
    session.refresh(invoice)
    return invoice
