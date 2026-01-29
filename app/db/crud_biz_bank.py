from fastapi import HTTPException, status
from sqlmodel import Session, select
from app.db import conn, model_biz_bank


ModelTable = model_biz_bank.Biz_Bank


def get_all(offset1: int = 0, limit1: int = 20, db: Session = None):
    all = db.exec(select(ModelTable).offset(offset1).limit(limit1)).all()
    return all


def get_one(id: int, db: Session = None):
    one = db.get(ModelTable, id)
    if not one:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Biz not found with id: {id}",
        )
    return one

def create_one(Obj: model_biz_bank.BizBankCreate, db: Session = None):
    Obj_2_db = ModelTable.model_validate(Obj)
    db.add(Obj_2_db)
    db.commit()
    db.refresh(Obj_2_db)
    return Obj_2_db


def update_one(id: int, BizBank: model_biz_bank.BizBankUpdate, db: Session = None):
    Biz_to_update = db.get(ModelTable, id)
    if not Biz_to_update:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Biz not found with id: {id}",
        )

   
    for field, value in BizBank.model_dump(exclude_unset=True).items():
            setattr(Biz_to_update, field, value)

    db.add(Biz_to_update)
    db.commit()
    db.refresh(Biz_to_update)
    return Biz_to_update


def delete_one(id: int, db: Session = None):
    OneObj  = db.get(ModelTable, id)
    if not OneObj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Hero not found with id: {id}",
        )

    db.delete(OneObj)
    db.commit()
    return {"ok": True}
