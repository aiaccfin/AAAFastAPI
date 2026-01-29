from typing import Any, Dict
from fastapi import APIRouter, Body, HTTPException
from bson import ObjectId
from datetime import datetime, date

from app.db.x_mg_conn import coa_collection
from app.utils.u_sequence import get_next_sequence

router = APIRouter()


def convert_dates(document: dict):
    """Converts all date fields to datetime for MongoDB compatibility"""
    for key, value in document.items():
        if isinstance(value, date) and not isinstance(value, datetime):
            document[key] = datetime.combine(value, datetime.min.time())
    return document


# -----------------------------
# Create coa
# -----------------------------
@router.post("/coa", response_model=Dict[str, Any], status_code=201)
async def create_coa(
    data: Dict[str, Any] = Body(
        ...,
        example = { 
                "id": 1,
                "coa_id": 1100,
                "biz_type": 11,
                "account_type": "Assets",
                "account_subtype": "Cash and Bank",
                "parent_account": "1000 Cash and Cash Equivalents",
                "sub_account": "1030 Short-Term Investments",
                "status": "Active",
                "coa_note": "Short-term investments"
        }
    )
):
    data = convert_dates(data)
    data["is_active"] = True
    data["coa_id"] = await get_next_sequence("coa_id")

    result = await coa_collection.insert_one(data)
    data["id"] = str(result.inserted_id)
    data.pop("_id", None)

    return data


# -----------------------------
# Read/Get coa by ID
# -----------------------------
@router.get("/coa/{coa_id}", response_model=Dict[str, Any])
async def get_coa(coa_id: str):
    coa = await coa_collection.find_one({"_id": ObjectId(coa_id)})
    if not coa:
        raise HTTPException(status_code=404, detail="coa not found")

    coa["id"] = str(coa["_id"])
    coa.pop("_id", None)
    return coa


# -----------------------------
# Update coa by ID
# -----------------------------
@router.put("/coa/{coa_id}", response_model=Dict[str, Any])
async def update_coa(coa_id: str, data: Dict[str, Any] = Body(...)):
    data = convert_dates(data)
    updated = await coa_collection.find_one_and_update(
        {"_id": ObjectId(coa_id)},
        {"$set": data},
        return_document=True
    )

    if not updated:
        raise HTTPException(status_code=404, detail="coa not found")

    updated["id"] = str(updated["_id"])
    updated.pop("_id", None)
    return updated


# -----------------------------
# Delete coa by ID
# -----------------------------
@router.delete("/coa/{coa_id}", response_model=Dict[str, Any])
async def delete_coa(coa_id: str):
    deleted = await coa_collection.find_one_and_delete({"_id": ObjectId(coa_id)})
    if not deleted:
        raise HTTPException(status_code=404, detail="coa not found")

    deleted["id"] = str(deleted["_id"])
    deleted.pop("_id", None)
    return deleted


# -----------------------------
# List all coa
# -----------------------------
@router.get("/coa", response_model=Dict[str, Any])
async def list_coa():
    cursor = coa_collection.find()
    coa = []
    async for doc in cursor:
        doc["id"] = str(doc["_id"])
        doc.pop("_id", None)
        coa.append(doc)
    return {"coa": coa}
