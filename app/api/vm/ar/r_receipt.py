from typing import List
from fastapi import APIRouter, HTTPException
from datetime import datetime
from bson import ObjectId  # from the 'bson' package that comes with pymongo/motor

from pydantic import BaseModel, Field
from app.schemas.s_receipt import Receipt
from app.db.x_mg_conn import receipt_collection

router = APIRouter()

def to_object_id(id_str: str) -> ObjectId:
    if not ObjectId.is_valid(id_str):
        raise HTTPException(status_code=400, detail="Invalid receipt id")
    return ObjectId(id_str)


@router.post("/", response_model=Receipt)
async def create_receipt(receipt: Receipt):
    receipt_data = receipt.dict()
    receipt_data["created_at"] = datetime.utcnow()

    result = await receipt_collection.insert_one(receipt_data)
    if not result.inserted_id:
        raise HTTPException(status_code=500, detail="Receipt could not be created")

    # return JSON-friendly _id (string) for the client
    receipt_data["_id"] = str(result.inserted_id)
    return receipt_data


@router.get("/", response_model=List[Receipt])
async def get_receipts():
    receipts = await receipt_collection.find().to_list(length=100)
    for r in receipts:
        if "_id" in r:
            r["_id"] = str(r["_id"])
    return receipts


@router.get("/{receipt_id}", response_model=Receipt)
async def get_receipt(receipt_id: str):
    obj_id = to_object_id(receipt_id)
    receipt = await receipt_collection.find_one({"_id": obj_id})
    if not receipt:
        raise HTTPException(status_code=404, detail="Receipt not found")
    receipt["_id"] = str(receipt["_id"])
    return receipt


@router.put("/{receipt_id}", response_model=Receipt)
async def update_receipt(receipt_id: str, receipt: Receipt):
    obj_id = to_object_id(receipt_id)
    update_data = receipt.dict(exclude_unset=True)

    # Avoid trying to set _id (immutable)
    update_data.pop("_id", None)

    update_data["updated_at"] = datetime.utcnow()

    result = await receipt_collection.update_one({"_id": obj_id}, {"$set": update_data})
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Receipt not found")

    updated = await receipt_collection.find_one({"_id": obj_id})
    updated["_id"] = str(updated["_id"])
    return updated


@router.delete("/{receipt_id}")
async def delete_receipt(receipt_id: str):
    obj_id = to_object_id(receipt_id)
    result = await receipt_collection.delete_one({"_id": obj_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Receipt not found")
    return {"detail": "Receipt deleted successfully"}



# from typing import List
# from fastapi import APIRouter, HTTPException
# from datetime import datetime

# from pydantic import BaseModel, Field

# # Import Transaction schema (you’ll need to define this similar to InvoiceItem)
# from app.schemas.s_receipt import Receipt
# from app.db.x_mg_conn import receipt_collection  # new MongoDB collection for receipts

# router = APIRouter()

# # ----------- CREATE RECEIPT (Flexible JSON) -----------  
# @router.post("/", response_model=Receipt)
# async def create_receipt(receipt: Receipt):
#     receipt_data = receipt.dict()
#     receipt_data["created_at"] = datetime.utcnow()

#     result = await receipt_collection.insert_one(receipt_data)
#     if not result.inserted_id:
#         raise HTTPException(status_code=500, detail="Receipt could not be created")

#     receipt_data["_id"] = str(result.inserted_id)
#     return receipt_data


# # ----------- GET ALL RECEIPTS -----------  
# @router.get("/", response_model=List[Receipt])
# async def get_receipts():
#     receipts = await receipt_collection.find().to_list(100)

#     # convert MongoDB ObjectId to string
#     for receipt in receipts:
#         if "_id" in receipt:
#             receipt["_id"] = str(receipt["_id"])

#     return receipts


# # ----------- GET SINGLE RECEIPT -----------  
# @router.get("/{receipt_id}", response_model=Receipt)
# async def get_receipt(receipt_id: str):
#     receipt = await receipt_collection.find_one({"_id": receipt_id})
#     if not receipt:
#         raise HTTPException(status_code=404, detail="Receipt not found")

#     if "_id" in receipt:
#         receipt["_id"] = str(receipt["_id"])

#     return receipt


# # ----------- UPDATE RECEIPT (Flexible JSON) -----------  
# @router.put("/{receipt_id}", response_model=Receipt)
# async def update_receipt(receipt_id: str, receipt: Receipt):
#     update_data = receipt.dict(exclude_unset=True)
#     update_data["updated_at"] = datetime.utcnow()

#     result = await receipt_collection.update_one(
#         {"_id": receipt_id}, {"$set": update_data}
#     )

#     if result.matched_count == 0:
#         raise HTTPException(status_code=404, detail="Receipt not found")

#     updated_receipt = await receipt_collection.find_one({"_id": receipt_id})
#     if "_id" in updated_receipt:
#         updated_receipt["_id"] = str(updated_receipt["_id"])

#     return updated_receipt


# # ----------- DELETE RECEIPT (Hard Delete) -----------  
# @router.delete("/{receipt_id}")
# async def delete_receipt(receipt_id: str):
#     result = await receipt_collection.delete_one({"_id": receipt_id})
#     if result.deleted_count == 0:
#         raise HTTPException(status_code=404, detail="Receipt not found")
#     return {"detail": "Receipt deleted successfully"}