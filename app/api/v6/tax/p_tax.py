from fastapi import APIRouter, Depends, File, UploadFile, HTTPException, UploadFile, Form 

from sqlmodel import Session, select

from app.db.pg.crud  import c_tax
from app.db.pg.model  import m_tax
from app.db.pg.p_conn import get_session_no_yield


router = APIRouter()

@router.get("/")
def get_all(db: Session = Depends(get_session_no_yield),):
    return c_tax.get_all( db)


@router.get("/{one_id}")
def get_one(one_id: int, db: Session = Depends(get_session_no_yield)):
    return c_tax.get_one(one_id=one_id, db=db)

@router.post("/new")
def post_new_tax(tax: m_tax.TaxCreate, db: Session = Depends(get_session_no_yield)):
    return c_tax.create_tax(tax=tax, db=db)

@router.patch("/{one_id}")
def update_1_tax(one_id: int, tax: m_tax.TaxUpdate, db: Session = Depends(get_session_no_yield)):
    return c_tax.update_tax(one_id=one_id, tax=tax, db=db)


@router.delete("/{one_id}")
def delete_1_tax(one_id: int, db: Session = Depends(get_session_no_yield)):
    return c_tax.delete_tax(one_id=one_id, db=db)


