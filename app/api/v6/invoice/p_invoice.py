from fastapi import APIRouter, Depends, File, UploadFile, HTTPException, UploadFile, Form 

from sqlmodel import Session, select

from app.db.pg.crud  import c_invoice
from app.db.pg.model  import m_invoice
from app.db.pg.p_conn import get_session_no_yield
from app.services import s_inv, s_file_system
from app.utils import u_is_textpdf 


router = APIRouter()

@router.get("/")
def get_all(db: Session = Depends(get_session_no_yield),):
    return c_invoice.get_all( db)


@router.get("/{one_id}")
def get_one(one_id: int, db: Session = Depends(get_session_no_yield)):
    return c_invoice.get_one(one_id=one_id, db=db)

@router.post("/new")
def post_new_invoice(Invoice: m_invoice.InvoiceCreate, db: Session = Depends(get_session_no_yield)):
    return c_invoice.create_invoice(Invoice=Invoice, db=db)

@router.patch("/{one_id}")
def update_1_invoice(one_id: int, Invoice: m_invoice.InvoiceUpdate, db: Session = Depends(get_session_no_yield)):
    return c_invoice.update_invoice(one_id=one_id, Invoice=Invoice, db=db)


@router.delete("/{one_id}")
def delete_1_invoice(one_id: int, db: Session = Depends(get_session_no_yield)):
    return c_invoice.delete_invoice(one_id=one_id, db=db)


@router.post("/upload",)
async def ocr(oUploadFile: UploadFile = File(...), db: Session = Depends(get_session_no_yield)):
    print(f"Received file: {oUploadFile.filename}")
    try:
        pdf_name, pdf_folder = await s_file_system.save_upload_file(oUploadFile)

        if u_is_textpdf.is_textpdf(oUploadFile):
            _type = "text-pdf"
            inv_json = s_inv.inv_textpdf(oUploadFile, pdf_name, pdf_folder)
        else:
            _type = "img-pdf"
            inv_json = s_inv.inv_imgpdf(pdf_name, pdf_folder)

        print("DEBUG inv_json:", inv_json)
        
        # invoice_data = m_invoice.InvoiceCreate.model_validate(inv_json["content"])
        invoice_data = m_invoice.InvoiceCreate.model_validate(inv_json)

        saved_invoice = c_invoice.create_invoice(invoice_data, db)
        
        return {"type": _type , "content": inv_json}
    
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing file: {str(e)}")


