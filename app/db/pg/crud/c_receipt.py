from fastapi import HTTPException, status
from sqlmodel import Session, select
from app.db.pg.model import m_receipt

def get_all(db: Session = None):
    all = db.exec(select(m_receipt.Receipt)).all()
    return all

def get_one(one_id: int, db: Session = None):
    one_receipt = db.get(m_receipt.Receipt, one_id)
    if not one_receipt:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"receipt not found with id: {one_id}",
        )
    return one_receipt

def create_receipt(receipt: m_receipt.ReceiptCreate, db: Session = None):
    receipt_to_db = m_receipt.Receipt.model_validate(receipt)
    db.add(receipt_to_db)
    db.commit()
    db.refresh(receipt_to_db)
    return receipt_to_db

def create_receipt_from_upload(receipt_create: m_receipt.ReceiptCreate, db: Session = None):
    receipt_to_db = m_receipt.Receipt(**receipt_create.model_dump(exclude={"id"}))
    db.add(receipt_to_db)
    db.commit()
    db.refresh(receipt_to_db)
    return receipt_to_db



def update_receipt(one_id: int, receipt: m_receipt.ReceiptUpdate, db: Session = None):
    receipt_to_update = db.get(m_receipt.Receipt, one_id)
    if not receipt_to_update:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"receipt not found with id: {one_id}",
        )

    # if receipt.Receipt_note is not None:
    #         receipt_to_update.Receipt_note = receipt.Receipt_note

    for field, value in receipt.model_dump(exclude_unset=True).items():
            setattr(receipt_to_update, field, value)

    db.add(receipt_to_update)
    db.commit()
    db.refresh(receipt_to_update)
    return receipt_to_update


def delete_receipt(one_id: int, db: Session = None):
    receipt  = db.get(m_receipt.Receipt, one_id)
    if not receipt:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"receipt not found with id: {one_id}",
        )

    db.delete(receipt)
    db.commit()
    return {"ok": True}
