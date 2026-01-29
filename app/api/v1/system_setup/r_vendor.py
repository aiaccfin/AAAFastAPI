from typing import Any, Dict
from fastapi import APIRouter, Body, HTTPException
from bson import ObjectId
from datetime import datetime, date

from app.db.x_mg_conn import vendor_collection
from app.utils.u_sequence import get_next_sequence

router = APIRouter()


def convert_dates(document: dict):
    """Converts all date fields to datetime for MongoDB compatibility"""
    for key, value in document.items():
        if isinstance(value, date) and not isinstance(value, datetime):
            document[key] = datetime.combine(value, datetime.min.time())
    return document


# -----------------------------
# Create Vendor
# -----------------------------
@router.post("/vendor", response_model=Dict[str, Any], status_code=201)
async def create_vendor(
    data: Dict[str, Any] = Body(
        ...,
        example = {
            "name": "Vendor Name",
            "description": "Vendor Description",
            "contact_info": {
                "email": "vendor@example.com",
                "phone": "123-456-7890"
            },
            "address": {
                "street": "123 Vendor St",
                "city": "Vendor City",
                "state": "VC",
                "zip": "12345"
            }
        }
    )
):
    data = convert_dates(data)
    data["is_active"] = True
    data["vendor_id"] = await get_next_sequence("vendor_id")

    result = await vendor_collection.insert_one(data)
    data["id"] = str(result.inserted_id)
    data.pop("_id", None)

    return data


# -----------------------------
# Read/Get Vendor by ID
# -----------------------------
@router.get("/vendors/{vendor_id}", response_model=Dict[str, Any])
async def get_vendor(vendor_id: str):
    vendor = await vendor_collection.find_one({"_id": ObjectId(vendor_id)})
    if not vendor:
        raise HTTPException(status_code=404, detail="Vendor not found")

    vendor["id"] = str(vendor["_id"])
    vendor.pop("_id", None)
    return vendor


# -----------------------------
# Update Vendor by ID
# -----------------------------
@router.put("/vendors/{vendor_id}", response_model=Dict[str, Any])
async def update_vendor(vendor_id: str, data: Dict[str, Any] = Body(...)):
    data = convert_dates(data)
    updated = await vendor_collection.find_one_and_update(
        {"_id": ObjectId(vendor_id)},
        {"$set": data},
        return_document=True
    )

    if not updated:
        raise HTTPException(status_code=404, detail="Product not found")

    updated["id"] = str(updated["_id"])
    updated.pop("_id", None)
    return updated


# -----------------------------
# Delete Vendor by ID
# -----------------------------
@router.delete("/vendors/{vendor_id}", response_model=Dict[str, Any])
async def delete_vendor(vendor_id: str):
    deleted = await vendor_collection.find_one_and_delete({"_id": ObjectId(vendor_id)})
    if not deleted:
        raise HTTPException(status_code=404, detail="Vendor not found")

    deleted["id"] = str(deleted["_id"])
    deleted.pop("_id", None)
    return deleted


# -----------------------------
# List all vendors
# -----------------------------
@router.get("/vendors", response_model=Dict[str, Any])
async def list_vendors():
    cursor = vendor_collection.find()
    vendors = []
    async for doc in cursor:
        doc["id"] = str(doc["_id"])
        doc.pop("_id", None)
        vendors.append(doc)
    return {"vendors": vendors}
