from typing  import Optional

from fastapi import APIRouter, Depends

from sqlmodel import Session, select

from app.db  import crud_coa, model_coa
from app.db.conn import get_session

router = APIRouter()


@router.get("/test-session")
def test_session(db: Session = Depends(get_session)):
    result = db.exec(select(model_coa.COA_Standard)).all()
    return {"data": result}


@router.get("/test")
def root(): return {"COA": "System Setup"}

@router.get("/")
def get_all_coa(offset1: Optional[int] = 0, limit1: Optional[int] = 20000000, db: Session = Depends(get_session),):
    return crud_coa.read_all_coa(offset1, limit1,  db)


@router.get("/{one_id}")
def get_one_coa(one_id: int, db: Session = Depends(get_session)):
    return crud_coa.read_one_coa(one_id=one_id, db=db)


@router.post("/new")
def post_new_coa(coa: model_coa.COACreate, db: Session = Depends(get_session)):
    return crud_coa.create_coa(COA=coa, db=db)


@router.patch("/{one_id}")
def update_a_hero(one_id: int, coa: model_coa.COAUpdate, db: Session = Depends(get_session)):
    return crud_coa.update_coa(one_id=one_id, COA=coa, db=db)


@router.delete("/{one_id}")
def delete_a_hero(one_id: int,          db: Session = Depends(get_session)):
    return crud_coa.delete_coa(one_id=one_id, db=db)
