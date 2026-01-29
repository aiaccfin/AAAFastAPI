from app.api.p1.global_set.global_coa import get_coa
from app.db.models.mo_journal_header import JournalEntryDB
from app.db.models.mo_journal_line import JournalLineDB
from app.models.rls.m_invoice_rls import InvoiceDB


from app.api.p1.global_set.global_coa import get_coa


def create_invoice_journal(session, invoice: InvoiceDB):
    ar = get_coa(session, invoice.tenant_id, "1100")       # Accounts Receivable
    revenue = get_coa(session, invoice.tenant_id, "4000")  # Revenue
    tax = get_coa(session, invoice.tenant_id, "2100")      # Tax Payable

    entry = JournalEntryDB(
        tenant_id=invoice.tenant_id,
        source_type="invoice",
        source_id=invoice.id,
        entry_date=invoice.issue_date,
        memo=f"Invoice {invoice.invoice_number}"
    )

    entry.lines.append(
        JournalLineDB(
            coa_id=ar.id,
            debit=invoice.total_amount,
            credit=0
        )
    )

    entry.lines.append(
        JournalLineDB(
            coa_id=revenue.id,
            debit=0,
            credit=invoice.discounted_subtotal
        )
    )

    if invoice.tax_amount > 0:
        entry.lines.append(
            JournalLineDB(
                coa_id=tax.id,
                debit=0,
                credit=invoice.tax_amount
            )
        )

    session.add(entry)
