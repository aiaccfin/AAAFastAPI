from fastapi import HTTPException, status
from sqlmodel import Session, select
from app.db.pg.model import m_invoice

def get_all(db: Session = None):
    all = db.exec(select(m_invoice.Invoice)).all()
    return all

def get_one(one_id: int, db: Session = None):
    one_invoice = db.get(m_invoice.Invoice, one_id)
    if not one_invoice:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Invoice not found with id: {one_id}",
        )
    return one_invoice

# def create_invoice(Invoice: m_invoice.InvoiceCreate, db: Session = None):
#     Invoice_to_db = m_invoice.Invoice.model_validate(Invoice)
#     db.add(Invoice_to_db)
#     db.commit()
#     db.refresh(Invoice_to_db)
#     return Invoice_to_db

def create_invoice(invoice_create: m_invoice.InvoiceCreate, db: Session = None):
    invoice_to_db = m_invoice.Invoice(**invoice_create.model_dump(exclude={"id"}))
    db.add(invoice_to_db)
    db.commit()
    db.refresh(invoice_to_db)
    return invoice_to_db



def update_invoice(one_id: int, Invoice: m_invoice.InvoiceUpdate, db: Session = None):
    Invoice_to_update = db.get(m_invoice.Invoice, one_id)
    if not Invoice_to_update:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Invoice not found with id: {one_id}",
        )

    # if Invoice.Invoice_note is not None:
    #         Invoice_to_update.Invoice_note = Invoice.Invoice_note

    for field, value in Invoice.model_dump(exclude_unset=True).items():
            setattr(Invoice_to_update, field, value)

    db.add(Invoice_to_update)
    db.commit()
    db.refresh(Invoice_to_update)
    return Invoice_to_update


def delete_invoice(one_id: int, db: Session = None):
    Invoice  = db.get(m_invoice.Invoice, one_id)
    if not Invoice:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Invoice not found with id: {one_id}",
        )

    db.delete(Invoice)
    db.commit()
    return {"ok": True}
