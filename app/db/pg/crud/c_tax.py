from fastapi import HTTPException, status
from sqlmodel import Session, select
from app.db.pg.model import m_tax

def get_all(db: Session = None):
    all = db.exec(select(m_tax.Tax)).all()
    return all

def get_one(one_id: int, db: Session = None):
    one_tax = db.get(m_tax.Tax, one_id)
    if not one_tax:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"tax not found with id: {one_id}",
        )
    return one_tax

def create_tax(tax: m_tax.TaxCreate, db: Session = None):
    tax_to_db = m_tax.Tax.model_validate(tax)
    db.add(tax_to_db)
    db.commit()
    db.refresh(tax_to_db)
    return tax_to_db

def create_tax_from_upload(tax_create: m_tax.TaxCreate, db: Session = None):
    tax_to_db = m_tax.Tax(**tax_create.model_dump(exclude={"id"}))
    db.add(tax_to_db)
    db.commit()
    db.refresh(tax_to_db)
    return tax_to_db



def update_tax(one_id: int, tax: m_tax.TaxUpdate, db: Session = None):
    tax_to_update = db.get(m_tax.Tax, one_id)
    if not tax_to_update:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"tax not found with id: {one_id}",
        )

    # if tax.Tax_note is not None:
    #         tax_to_update.Tax_note = tax.Tax_note

    for field, value in tax.model_dump(exclude_unset=True).items():
            setattr(tax_to_update, field, value)

    db.add(tax_to_update)
    db.commit()
    db.refresh(tax_to_update)
    return tax_to_update


def delete_tax(one_id: int, db: Session = None):
    tax  = db.get(m_tax.Tax, one_id)
    if not tax:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"tax not found with id: {one_id}",
        )

    db.delete(tax)
    db.commit()
    return {"ok": True}
