from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List
from pathlib import Path
from fastapi.responses import JSONResponse
import os
router = APIRouter()

BASE_DIR = Path("./tmp")
DEFAULT_FOLDER = Path("./tmp")

class FolderCreateRequest(BaseModel):
    folder_name: str


@router.get("/listfolder/{folder_name:path}")
def list_specific_folder(folder_name: str):
    cwd = Path(os.getcwd())
    target_folder = cwd / folder_name

    if not target_folder.exists():
        return {"error": f"Folder '{folder_name}' not found in {cwd}"}

    files = []
    for item in target_folder.iterdir():
        files.append({
            "name": item.name,
            "type": "directory" if item.is_dir() else "file",
            "size": item.stat().st_size,
            "last_modified": item.stat().st_mtime
        })

    return {
        "cwd": str(cwd),
        "target_folder": str(target_folder),
        "items": files
    }



@router.get("/list-current")
def list_current_directory():
    cwd = os.getcwd()
    files = os.listdir(cwd)
    return {"cwd": cwd, "files": files}


@router.get("/list-tmp")
def list_jack_directory():
    if not BASE_DIR.exists():
        return JSONResponse(content={"error": "Directory not found."}, status_code=404)

    items = []
    for item in BASE_DIR.iterdir():
        items.append({
            "name": item.name,
            "type": "directory" if item.is_dir() else "file",
            "size": item.stat().st_size,
            "last_modified": item.stat().st_mtime
        })

    return {"items": items}


@router.post("/create_folder")
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
