from typing import Any, Dict
from fastapi import APIRouter, Body, HTTPException
from bson import ObjectId
from datetime import datetime, date

from app.db.x_mg_conn import customer_collection
from app.utils.u_sequence import get_next_sequence

router = APIRouter()


def convert_dates(document: dict):
    """Converts all date fields to datetime for MongoDB compatibility"""
    for key, value in document.items():
        if isinstance(value, date) and not isinstance(value, datetime):
            document[key] = datetime.combine(value, datetime.min.time())
    return document


# -----------------------------
# Create customer
# -----------------------------
@router.post("/customer", response_model=Dict[str, Any], status_code=201)
async def create_customer(
    data: Dict[str, Any] = Body(
        ...,
        example = {
            "name": "customer Name",
            "description": "customer Description",
            "contact_info": {
                "email": "customer@example.com",
                "phone": "123-456-7890"
            },
            "address": {
                "street": "123 customer St",
                "city": "customer City",
                "state": "VC",
                "zip": "12345"
            }
        }
    )
):
    data = convert_dates(data)
    data["is_active"] = True
    data["customer_id"] = await get_next_sequence("customer_id")

    result = await customer_collection.insert_one(data)
    data["id"] = str(result.inserted_id)
    data.pop("_id", None)

    return data


# -----------------------------
# Read/Get customer by ID
# -----------------------------
@router.get("/customers/{customer_id}", response_model=Dict[str, Any])
async def get_customer(customer_id: str):
    customer = await customer_collection.find_one({"_id": ObjectId(customer_id)})
    if not customer:
        raise HTTPException(status_code=404, detail="customer not found")

    customer["id"] = str(customer["_id"])
    customer.pop("_id", None)
    return customer


# -----------------------------
# Update customer by ID
# -----------------------------
@router.put("/customers/{customer_id}", response_model=Dict[str, Any])
async def update_customer(customer_id: str, data: Dict[str, Any] = Body(...)):
    data = convert_dates(data)
    updated = await customer_collection.find_one_and_update(
        {"_id": ObjectId(customer_id)},
        {"$set": data},
        return_document=True
    )

    if not updated:
        raise HTTPException(status_code=404, detail="Product not found")

    updated["id"] = str(updated["_id"])
    updated.pop("_id", None)
    return updated


# -----------------------------
# Delete customer by ID
# -----------------------------
@router.delete("/customers/{customer_id}", response_model=Dict[str, Any])
async def delete_customer(customer_id: str):
    deleted = await customer_collection.find_one_and_delete({"_id": ObjectId(customer_id)})
    if not deleted:
        raise HTTPException(status_code=404, detail="customer not found")

    deleted["id"] = str(deleted["_id"])
    deleted.pop("_id", None)
    return deleted


# -----------------------------
# List all customers
# -----------------------------
@router.get("/customers", response_model=Dict[str, Any])
async def list_customers():
    cursor = customer_collection.find()
    customers = []
    async for doc in cursor:
        doc["id"] = str(doc["_id"])
        doc.pop("_id", None)
        customers.append(doc)
    return {"customers": customers}
