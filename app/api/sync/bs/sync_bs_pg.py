import glob
import os
from fastapi import APIRouter, Depends, File, UploadFile, HTTPException, UploadFile, Form , BackgroundTasks
import logging

from sqlmodel import Session, select
import mimetypes
from starlette.status import HTTP_415_UNSUPPORTED_MEDIA_TYPE

from app.db.pg.crud  import c_bs
from app.db.pg.model  import m_bs, m_bs_ai
from app.db.pg.p_conn import get_session_no_yield
from app.services import s_bs, s_file_system
from app.utils import u_is_textpdf 

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
console_handler = logging.StreamHandler()  # StreamHandler for console output
console_handler.setLevel(logging.INFO)  # Set the level for the console
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
console_handler.setFormatter(formatter)

# Add the handler to the logger
logger.addHandler(console_handler)

# Test logging
logger.info("Logger is now set up correctly.")
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
def get_one(one_id: str, db: Session = Depends(get_session_no_yield)):
    summary = c_bs.get_one_summary_uuid(uuid_string=one_id, db=db)
    detail =  c_bs.get_one_detail_based_on_summary_uuid(uuid_string=one_id, db=db)
    return {
        "summary": summary,
        "detail": detail
    }


@router.get("/checkid/{one_id}")
async def check_file(one_id: str):
    upload_folder = os.path.abspath("./tmp/v6")
    done_folder = os.path.abspath("./tmp/done")

    # Check upload folder
    upload_pattern = os.path.join(upload_folder, f"{one_id}*")
    upload_matches = glob.glob(upload_pattern)

    if upload_matches:
        # Check done folder too
        done_pattern = os.path.join(done_folder, f"{one_id}.*")
        done_matches = glob.glob(done_pattern)

        if done_matches:
            return {
                "code": 1,
                "status": "content ready",
                "files": one_id,
            }
        else:
            return {
                "code": 4002,
                "status": "content not ready",
                "id": one_id,
                "files": one_id,
            }

    # If not found in upload folder
    return {
        "code": 4001,
        "status": "uid not exist",
        "id": one_id,
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
async def bs_upload(oUploadFile: UploadFile = File(...),):
    try:
        logger.info(f"Received file: {oUploadFile.filename}")
        
        uuid_name, upload_folder, upload_name_uuid = await s_file_system.save_upload_file_2_uuid(oUploadFile)
        logger.info(f" ------------ File saved with UUID: {uuid_name}, File Name: {upload_name_uuid}")

        return {
            "status: ": "success",
            "unique id: ": uuid_name,
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Server error: {str(e)}")
    

async def process_file(oUploadFile: UploadFile, pdf_folder: str, pdf_file_name: str, uuid_name: str, db: Session):
    try:
        # Process based on PDF type
        if u_is_textpdf.is_textpdf(oUploadFile):
            bs_data = s_bs.bs_textpdf(oUploadFile, pdf_file_name, pdf_folder)
            _type = "text-pdf"
        else:
            bs_data = s_bs.bs_imgpdf(pdf_file_name, pdf_folder)
            _type = "img-pdf"

        if not bs_data:
            raise HTTPException(status_code=400, detail="Failed to process PDF")

        # Save to database
        print(f"print ---- UUID: {uuid_name} -- Processed file: {oUploadFile.filename}, Type: {_type}")
        result = c_bs.save_parsed_bs_uuid(bs_data, uuid_name, db)
        logger.warning(f"UUID: {uuid_name} -- Processed file: {oUploadFile.filename}, Type: {_type}")

    except Exception as e:
        logger.error(f"Error processing file {oUploadFile.filename}: {str(e)}")