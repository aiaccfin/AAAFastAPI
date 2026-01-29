from fastapi import APIRouter, Depends, File, UploadFile, HTTPException, UploadFile, Form 

from sqlmodel import Session, select
import mimetypes
from starlette.status import HTTP_415_UNSUPPORTED_MEDIA_TYPE

from app.db.pg.crud  import c_receipt
from app.db.pg.model  import m_receipt
from app.db.pg.p_conn import get_session_no_yield
from app.services import s_receipt, s_file_system
from app.utils import u_is_textpdf 

router = APIRouter()

@router.get("/")
def get_all(db: Session = Depends(get_session_no_yield),):
    return c_receipt.get_all(db)

@router.get("/{one_id}")
def get_one(one_id: int, db: Session = Depends(get_session_no_yield)):
    return c_receipt.get_one(one_id=one_id, db=db)

@router.post("/new")
def post_new_receipt(receipt: m_receipt.ReceiptCreate, db: Session = Depends(get_session_no_yield)):
    return c_receipt.create_receipt(receipt=receipt, db=db)

@router.patch("/{one_id}")
def update_1_receipt(one_id: int, receipt: m_receipt.ReceiptUpdate, db: Session = Depends(get_session_no_yield)):
    return c_receipt.update_receipt(one_id=one_id, receipt=receipt, db=db)


@router.delete("/{one_id}")
def delete_1_receipt(one_id: int, db: Session = Depends(get_session_no_yield)):
    return c_receipt.delete_receipt(one_id=one_id, db=db)


@router.post("/upload",)
async def ocr(oUploadFile: UploadFile = File(...), db: Session = Depends(get_session_no_yield)):
    print(f"Received file: {oUploadFile.filename}")
    try:
        # Step 1: Save the uploaded file
        pdf_name, pdf_folder = await s_file_system.save_upload_file(oUploadFile)

        # Step 2: Determine file type
        content_type = oUploadFile.content_type or mimetypes.guess_type(oUploadFile.filename)[0]
        print(f"Detected content type: {content_type}")

        if content_type == "application/pdf":
            if u_is_textpdf.is_textpdf(oUploadFile):
                _type = "text-pdf"
                receipt_json = s_receipt.receipt_textpdf(oUploadFile, pdf_name, pdf_folder)
            else:
                _type = "img-pdf"
                receipt_json = s_receipt.receipt_imgpdf(pdf_name, pdf_folder)

        # elif content_type and content_type.startswith("image/"):
        #     _type = "image"
        #     receipt_json = s_receipt.receipt_image(oUploadFile, pdf_name, pdf_folder)

        # elif content_type and content_type.startswith("text/"):
        #     _type = "text"
        #     receipt_json = s_receipt.receipt_text(oUploadFile, pdf_name, pdf_folder)

        else:
            raise HTTPException(
                status_code=HTTP_415_UNSUPPORTED_MEDIA_TYPE,
                detail=f"Unsupported file type: {content_type}"
            )

        print("DEBUG receipt_json:", receipt_json)
        receipt_data = m_receipt.ReceiptCreate.model_validate(receipt_json)
        saved_receipt = c_receipt.create_receipt_from_upload(receipt_data, db)

        return {"type": _type, "content": receipt_json}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing file: {str(e)}")