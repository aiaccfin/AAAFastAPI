from typing  import Optional
from fastapi import APIRouter, Depends
from sqlmodel import Session, select

from app.db  import conn, crud_biz_entity, model_biz_entity

router = APIRouter()


@router.get("/test")
def root(): return {"Biz Entity": "System Setup"}

@router.get("/")
def get_all(offset1: Optional[int] = 0, limit1: Optional[int] = 20000000, db: Session = Depends(conn.get_session),):
    return crud_biz_entity.get_all(offset1, limit1,  db)


@router.get("/{id}")
def get_one(id: int, db: Session = Depends(conn.get_session)):
    return crud_biz_entity.get_one(id=id, db=db)


@router.post("/new")
def post_new_biz_entity(Biz_Entity: model_biz_entity.BizEntityCreate, db: Session = Depends(conn.get_session)):
    return crud_biz_entity.create_biz_entity(Biz_Entity=Biz_Entity, db=db)