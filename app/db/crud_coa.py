from fastapi import HTTPException, status
from sqlmodel import Session, select
from app.db import conn, model_coa

def read_all_coa(offset1: int = 0, limit1: int = 20, db: Session = None):
    print(offset1 + limit1)
    all_coa = db.exec(select(model_coa.COA_Standard).offset(offset1).limit(limit1)).all()
    return all_coa

def read_one_coa(one_id: int, db: Session = None):
    one_coa = db.get(model_coa.COA_Standard, one_id)
    if not one_coa:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"COA not found with id: {one_id}",
        )
    return one_coa

def create_coa(COA: model_coa.COACreate, db: Session = None):
    COA_to_db = model_coa.COA_Standard.model_validate(COA)
    db.add(COA_to_db)
    db.commit()
    db.refresh(COA_to_db)
    return COA_to_db


def update_coa(one_id: int, COA: model_coa.COAUpdate, db: Session = None):
    COA_to_update = db.get(model_coa.COA_Standard, one_id)
    if not COA_to_update:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"COA not found with id: {one_id}",
        )

    # if COA.coa_note is not None:
    #         COA_to_update.coa_note = COA.coa_note
    
    for field, value in COA.model_dump(exclude_unset=True).items():
            setattr(COA_to_update, field, value)

    db.add(COA_to_update)
    db.commit()
    db.refresh(COA_to_update)
    return COA_to_update


def delete_coa(one_id: int, db: Session = None):
    coa  = db.get(model_coa.COA_Standard, one_id)
    if not coa:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Hero not found with id: {one_id}",
        )

    db.delete(coa)
    db.commit()
    return {"ok": True}
