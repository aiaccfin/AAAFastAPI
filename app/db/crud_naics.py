from fastapi import HTTPException, status
from sqlmodel import Session, select
from app.db import conn, model_naics

def get_all(db: Session = None):
    all = db.exec(select(model_naics.Naics_Standard)).all()
    return all

def get_one(one_id: int, db: Session = None):
    one_naics = db.get(model_naics.Naics_Standard, one_id)
    if not one_naics:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Naics not found with id: {one_id}",
        )
    return one_naics

def create_naics(Naics: model_naics.NaicsCreate, db: Session = None):
    Naics_to_db = model_naics.Naics_Standard.model_validate(Naics)
    db.add(Naics_to_db)
    db.commit()
    db.refresh(Naics_to_db)
    return Naics_to_db


def update_naics(one_id: int, Naics: model_naics.NaicsUpdate, db: Session = None):
    Naics_to_update = db.get(model_naics.Naics_Standard, one_id)
    if not Naics_to_update:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Naics not found with id: {one_id}",
        )

    # if Naics.Naics_note is not None:
    #         Naics_to_update.Naics_note = Naics.Naics_note
    
    for field, value in Naics.model_dump(exclude_unset=True).items():
            setattr(Naics_to_update, field, value)

    db.add(Naics_to_update)
    db.commit()
    db.refresh(Naics_to_update)
    return Naics_to_update


def delete_naics(one_id: int, db: Session = None):
    Naics  = db.get(model_naics.Naics_Standard, one_id)
    if not Naics:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Hero not found with id: {one_id}",
        )

    db.delete(Naics)
    db.commit()
    return {"ok": True}
