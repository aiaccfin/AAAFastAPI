from fastapi import APIRouter, Depends, File, UploadFile, HTTPException, UploadFile, Form , BackgroundTasks
import logging

from sqlmodel import Session, select
from starlette.status import HTTP_415_UNSUPPORTED_MEDIA_TYPE

from app.services import s_bs, s_file_system
from app.utils import u_is_textpdf 

from typing import Any, Dict
from fastapi import APIRouter, Body, HTTPException
from bson import ObjectId
from datetime import datetime, date

from app.db.x_mg_conn import bs_collection

router = APIRouter()


def convert_dates(document: dict):
    """Converts all date fields to datetime for MongoDB compatibility"""
    for key, value in document.items():
        if isinstance(value, date) and not isinstance(value, datetime):
            document[key] = datetime.combine(value, datetime.min.time())
    return document



logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
console_handler = logging.StreamHandler()  # StreamHandler for console output
console_handler.setLevel(logging.INFO)  # Set the level for the console
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
console_handler.setFormatter(formatter)

# Add the handler to the logger
logger.addHandler(console_handler)

router = APIRouter()


@router.post("/upload")
async def bs_upload(oUploadFile: UploadFile = File(...),):
    try:
        uuid_name, upload_folder, upload_name_uuid = await s_file_system.save_upload_file_2_uuid(oUploadFile)

        return {
            "status: ": "success",
            "unique id: ": uuid_name,
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Server error: {str(e)}")
    

# -----------------------------
# Read/Get Bank Statement by ID
# -----------------------------
@router.get("/bankstatements/{pdf_name}", response_model=Dict)
async def get_bankstatement_by_pdf_name(pdf_name: str):
    # Query the bankstatements collection using pdf_name
    bankstatement = await bs_collection.find_one({"pdf_name": pdf_name})
    
    if not bankstatement:
        raise HTTPException(status_code=404, detail="Bank statement not found")
    
    bankstatement["_id"] = str(bankstatement["_id"])
    # Return the found document
    return bankstatement


@router.get("/bankstatements", response_model=Dict[str, Any])
async def list_bank_statements():
    cursor = bs_collection.find()
    bank_statements = []
    async for doc in cursor:
        doc["_id"] = str(doc["_id"])
        bank_statements.append(doc)
    return {"bank_statements": bank_statements}
