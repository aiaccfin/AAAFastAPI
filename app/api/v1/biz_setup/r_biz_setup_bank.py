from typing  import Optional
from fastapi import APIRouter, Depends
from sqlmodel import Session, select

from app.db  import conn, crud_biz_bank, model_biz_bank

router = APIRouter()


@router.get("/test")
def root(): return {"Biz bank": "System Setup"}

@router.get("/")
def get_all(offset1: Optional[int] = 0, limit1: Optional[int] = 20000000, db: Session = Depends(conn.get_session),):
    return crud_biz_bank.get_all(offset1, limit1,  db)


@router.get("/{id}")
def get_one(id: int, db: Session = Depends(conn.get_session)):
    return crud_biz_bank.get_one(id=id, db=db)


# @router.post("/new")
# def post_new_biz_bank(biz_bank: model_biz_bank.BizBankCreate, db: Session = Depends(conn.get_session)):
#     return crud_biz_bank.create_one(biz_bank=biz_bank, db=db)

@router.post("/new")
def post_new_biz_bank(Obj: model_biz_bank.BizBankCreate, db: Session = Depends(conn.get_session)):
    return crud_biz_bank.create_one(Obj=Obj, db=db)