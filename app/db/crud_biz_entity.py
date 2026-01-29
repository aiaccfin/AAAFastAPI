from fastapi import HTTPException, status
from sqlmodel import Session, select
from app.db import conn, model_biz_entity


def get_all(offset1: int = 0, limit1: int = 20, db: Session = None):
    print(offset1 + limit1)
    all = db.exec(select(model_biz_entity.Biz_Entity).offset(offset1).limit(limit1)).all()
    return all

def get_one(id: int, db: Session = None):
    one_biz = db.get(model_biz_entity.Biz_Entity, id)
    if not one_biz:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Biz not found with id: {id}",
        )
    return one_biz

def create_biz_entity(BizEntity: model_biz_entity.BizEntityCreate, db: Session = None):
    Biz_to_db = model_biz_entity.Biz_Entity.model_validate(BizEntity)
    db.add(Biz_to_db)
    db.commit()
    db.refresh(Biz_to_db)
    return Biz_to_db


def update_biz_entity(one_id: int, BizEntity: model_biz_entity.BizEntityUpdate, db: Session = None):
    Biz_to_update = db.get(model_biz_entity.Biz_Entity, one_id)
    if not Biz_to_update:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Biz not found with id: {one_id}",
        )

    # if Biz.Biz_note is not None:
    #         Biz_to_update.Biz_note = Biz.Biz_note
    
    for field, value in BizEntity.model_dump(exclude_unset=True).items():
            setattr(Biz_to_update, field, value)

    db.add(Biz_to_update)
    db.commit()
    db.refresh(Biz_to_update)
    return Biz_to_update


def delete_biz_entity(one_id: int, db: Session = None):
    Biz  = db.get(model_biz_entity.Biz_Entity, one_id)
    if not Biz:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Hero not found with id: {one_id}",
        )

    db.delete(Biz)
    db.commit()
    return {"ok": True}
