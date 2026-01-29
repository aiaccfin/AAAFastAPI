from fastapi import APIRouter, Depends, File, UploadFile, HTTPException, UploadFile, Form 

from sqlmodel import Session, select
import mimetypes
from starlette.status import HTTP_415_UNSUPPORTED_MEDIA_TYPE

from app.db.pg.crud  import c_bs
from app.db.pg.model  import m_bs, m_bs_ai
from app.db.pg.p_conn import get_session_no_yield
from app.services import s_bs, s_file_system
from app.utils import u_is_textpdf 


router = APIRouter()

@router.get("/")
def get_all(db: Session = Depends(get_session_no_yield),):
    return c_bs.get_all( db)

@router.get("/summary")
def get_all_summary(db: Session = Depends(get_session_no_yield),):
    return c_bs.get_all_summary(db)


@router.get("/{one_id}")
def get_one(one_id: int, db: Session = Depends(get_session_no_yield)):
    return c_bs.get_one(one_id=one_id, db=db)


@router.get("/summary/{one_id}")
def get_one(one_id: int, db: Session = Depends(get_session_no_yield)):
    return c_bs.get_one_summary(one_id=one_id, db=db)


@router.get("/summaryanddetail/{one_id}")
def get_one(one_id: int, db: Session = Depends(get_session_no_yield)):
    summary = c_bs.get_one_summary(one_id=one_id, db=db)
    detail =  c_bs.get_one_detail_based_on_summary(one_id=one_id, db=db)
    return {
        "summary": summary,
        "detail": detail
    }


@router.post("/new")
def post_new_bs_detail(bs_detail: m_bs.BSDetailCreate, db: Session = Depends(get_session_no_yield)):
    return c_bs.create_bs_detail(bs_detail=bs_detail, db=db)

@router.patch("/{one_id}")
def update_1_bs_detail(one_id: int, bs_detail: m_bs.BSDetailUpdate, db: Session = Depends(get_session_no_yield)):
    return c_bs.update_bs_detail(one_id=one_id, bs_detail=bs_detail, db=db)


@router.delete("/{one_id}")
def delete_1_bs_detail(one_id: int, db: Session = Depends(get_session_no_yield)):
    return c_bs.delete_bs_detail(one_id=one_id, db=db)



@router.post("/upload")
async def bs_upload(
    oUploadFile: UploadFile = File(...), 
    db: Session = Depends(get_session_no_yield)
):
    try:
        print(f"Received file: {oUploadFile.filename}")
        
        # Save file
        pdf_name, pdf_folder = await s_file_system.save_upload_file(oUploadFile)

        # Process based on PDF type
        if u_is_textpdf.is_textpdf(oUploadFile):
            bs_data = s_bs.bs_textpdf(oUploadFile, pdf_name, pdf_folder)
            _type = "text-pdf"
        else:
            bs_data = s_bs.bs_imgpdf(pdf_name, pdf_folder)
            _type = "img-pdf"

        if not bs_data:
            raise HTTPException(status_code=400, detail="Failed to process PDF")

        # Save to database
        result = c_bs.save_parsed_bs(bs_data, db)

        return {
            "status": "success",
            "type": _type,
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Server error: {str(e)}")