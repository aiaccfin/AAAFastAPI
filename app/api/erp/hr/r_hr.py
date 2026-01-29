from fastapi import APIRouter, Depends

from sqlmodel import Session, select

from app.db  import crud_naics, model_naics
from app.db.pg.p_conn import get_session_no_yield

router = APIRouter()

@router.get("/test-session")
def test_session(db: Session = Depends(get_session_no_yield)):
    result = db.exec(select(model_naics.Naics_Standard)).all()
    return {"data": result}


@router.get("/test")
def root(): return {"Naics": "System Setup"}

@router.get("/")
def get_all(db: Session = Depends(get_session_no_yield),):
    return crud_naics.get_all( db)


@router.get("/{one_id}")
def get_one(one_id: int, db: Session = Depends(get_session_no_yield)):
    return crud_naics.get_one(one_id=one_id, db=db)


@router.post("/new")
def post_new_naics(Naics: model_naics.NaicsCreate, db: Session = Depends(get_session_no_yield)):
    return crud_naics.create_naics(Naics=Naics, db=db)

@router.patch("/{one_id}")
def update_1_naics(one_id: int, Naics: model_naics.NaicsUpdate, db: Session = Depends(get_session_no_yield)):
    return crud_naics.update_naics(one_id=one_id, Naics=Naics, db=db)


@router.delete("/{one_id}")
def delete_1_naics(one_id: int,          db: Session = Depends(get_session_no_yield)):
    return crud_naics.delete_naics(one_id=one_id, db=db)
