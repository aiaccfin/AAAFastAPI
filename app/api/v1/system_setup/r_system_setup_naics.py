from typing  import Optional

from fastapi import APIRouter, Depends

from sqlmodel import Session, select

from app.db  import crud_naics, model_naics
from app.db.conn import get_session

router = APIRouter()


@router.get("/test-session")
def test_session(db: Session = Depends(get_session)):
    result = db.exec(select(model_naics.Naics_Standard)).all()
    return {"data": result}


@router.get("/test")
def root(): return {"Naics": "System Setup"}

@router.get("/")
def get_all(offset1: Optional[int] = 0, limit1: Optional[int] = 20000000, db: Session = Depends(get_session),):
    return crud_naics.get_all(offset1, limit1,  db)


@router.get("/{one_id}")
def get_one(one_id: int, db: Session = Depends(get_session)):
    return crud_naics.get_one(one_id=one_id, db=db)


@router.post("/new")
def post_new_naics(Naics: model_naics.NaicsCreate, db: Session = Depends(get_session)):
    return crud_naics.create_naics(Naics=Naics, db=db)


@router.patch("/{one_id}")
def update_a_hero(one_id: int, Naics: model_naics.NaicsUpdate, db: Session = Depends(get_session)):
    return crud_naics.update_naics(one_id=one_id, Naics=Naics, db=db)


@router.delete("/{one_id}")
def delete_a_hero(one_id: int,          db: Session = Depends(get_session)):
    return crud_naics.delete_naics(one_id=one_id, db=db)
