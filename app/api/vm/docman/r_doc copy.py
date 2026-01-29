from fastapi import APIRouter, HTTPException
import os

from app.models.m_user import Role
from app.schemas.s_invoice import InvoiceModel
from app.schemas.s_email_reminder import EmailReminderRequest
from app.db.x_mg_conn import invoice_collection
from app.utils.u_load_invoice import load_invoice_from_file
from app.utils.gmail.senders.invoice_sender import send_invoice_reminder
from pydantic import BaseModel
from typing import List, Dict, Optional

router = APIRouter()

class FolderCreateRequest(BaseModel):
    folder_name: str

DEFAULT_FOLDER = os.path.abspath("./tmp")  # Now using absolute path

class FolderCreateRequest(BaseModel):
    folder_name: str
def scan_directory(base_path: str) -> List[Dict[str, str]]:
    """
    Recursively scan directory and return file tree with relative paths
    """
    items = []
    try:
        for root, dirs, files in os.walk(base_path):
            # Get relative path from DEFAULT_FOLDER
            rel_root = os.path.relpath(root, start=base_path)
            
            # Normalize for root directory
            if rel_root == ".":
                rel_root = ""

            # Add folders first
            for dir_name in dirs:
                items.append({
                    "path": os.path.join(rel_root, dir_name).replace("\\", "/"),
                    "type": "folder"
                })
            
            # Then add files
            for file_name in files:
                items.append({
                    "path": os.path.join(rel_root, file_name).replace("\\", "/"),
                    "type": "file"
                })
    except Exception as e:
        print(f"Error scanning {base_path}: {str(e)}")
    return items





@router.get("/files", response_model=List[Dict[str, str]])
def list_all_files():
    """
    List all files and folders recursively from the default directory
    Returns: List of dictionaries with 'path' (relative to DEFAULT_FOLDER) and 'type'
    """
    try:
        if not os.path.exists(DEFAULT_FOLDER):
            return []  # Return empty list if folder doesn't exist
            
        return scan_directory(DEFAULT_FOLDER)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    


@router.post("/folders")
def create_folder(request: FolderCreateRequest):
    """
    Create a new folder in the default directory
    """
    try:
        new_folder_path = os.path.join(DEFAULT_FOLDER, request.folder_name)

        if os.path.exists(new_folder_path):
            raise HTTPException(status_code=400, detail="Folder already exists")

        os.makedirs(new_folder_path)
        return {"message": f"Folder '{request.folder_name}' created successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Create default folder if it doesn't exist
os.makedirs(DEFAULT_FOLDER, exist_ok=True)
