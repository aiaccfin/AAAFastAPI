from typing import List
from fastapi import APIRouter, HTTPException
from datetime import datetime

from pydantic import BaseModel, Field

# Import InvoiceItem from your schema (already defined)
from app.schemas.s_invoice import InvoiceItem  
from app.db.x_mg_conn import item_collection  # assume you have a MongoDB collection

router = APIRouter()


# ----------- CREATE ITEM -----------
@router.post("/", response_model=InvoiceItem)
async def create_item(item: InvoiceItem):
    # Convert model to dict and insert into DB
    item_data = item.dict()

    result = await item_collection.insert_one(item_data)
    if not result.inserted_id:
        raise HTTPException(status_code=500, detail="Item could not be created")

    item_data["_id"] = str(result.inserted_id)
    return item_data



# ----------- GET ALL ITEMS -----------
@router.get("/", response_model=List[InvoiceItem])
async def get_items():
    items = await item_collection.find().to_list(100)

    # convert MongoDB ObjectId to string to avoid Pydantic serialization error
    for item in items:
        if "_id" in item:
            item["_id"] = str(item["_id"])

    return items


# ----------- GET SINGLE ITEM -----------
@router.get("/{item_id}", response_model=InvoiceItem)
async def get_item(item_id: str):
    item = await item_collection.find_one({"item_id": item_id})
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")

    # convert ObjectId to str
    if "_id" in item:
        item["_id"] = str(item["_id"])

    return item



# ----------- UPDATE ITEM -----------
@router.put("/{item_id}", response_model=InvoiceItem)
async def update_item(item_id: str, item: InvoiceItem):
    update_data = item.dict(exclude_unset=True)
    update_data["updated_at"] = datetime.utcnow()

    result = await item_collection.update_one(
        {"item_id": item_id}, {"$set": update_data}
    )

    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Item not found")

    updated_item = await item_collection.find_one({"item_id": item_id})
    return updated_item


# ----------- DELETE ITEM (Hard Delete) -----------
@router.delete("/{item_id}")
async def delete_item(item_id: str):
    result = await item_collection.delete_one({"item_id": item_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Item not found")
    return {"detail": "Item deleted successfully"}
