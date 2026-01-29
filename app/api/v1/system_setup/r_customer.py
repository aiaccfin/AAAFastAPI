from typing import Any, Dict
from fastapi import APIRouter, Body, HTTPException
from bson import ObjectId
from datetime import datetime

from app.db.x_mg_conn import customer_collection
from app.utils.u_sequence import get_next_sequence
from app.schemas.s_client import ClientCreate, ClientUpdate, ClientResponse  # Import your Pydantic models

router = APIRouter()


def convert_dates(document: dict):
    """Converts all date fields to datetime for MongoDB compatibility"""
    for key, value in document.items():
        if isinstance(value, datetime):
            document[key] = value.isoformat()  # Ensure date is ISO 8601 formatted
    return document


# -----------------------------
# Create customer
# -----------------------------
@router.post("/customer", response_model=ClientResponse, status_code=201)
async def create_customer(data: ClientCreate):
    data_dict = data.dict(exclude_unset=True)  # Only include fields that are set
    data_dict = convert_dates(data_dict)
    data_dict["is_active"] = True
    data_dict["customer_id"] = await get_next_sequence("customer_id")

    result = await customer_collection.insert_one(data_dict)
    data_dict["id"] = str(result.inserted_id)
    data_dict.pop("_id", None)

    return data_dict


# -----------------------------
# Read/Get customer by ID
# -----------------------------
@router.get("/customers/{customer_id}", response_model=ClientResponse)
async def get_customer(customer_id: str):
    customer = await customer_collection.find_one({"_id": ObjectId(customer_id)})
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")

    return customer


# -----------------------------
# Update customer by ID
# -----------------------------
@router.put("/customers/{customer_id}", response_model=ClientResponse)
async def update_customer(customer_id: str, data: ClientUpdate):
    data_dict = data.dict(exclude_unset=True)  # Only include fields that are updated
    data_dict = convert_dates(data_dict)
    updated = await customer_collection.find_one_and_update(
        {"_id": ObjectId(customer_id)},
        {"$set": data_dict},
        return_document=True
    )

    if not updated:
        raise HTTPException(status_code=404, detail="Customer not found")

    updated["id"] = str(updated["_id"])
    updated.pop("_id", None)
    return updated


# -----------------------------
# Delete customer by ID
# -----------------------------
@router.delete("/customers/{customer_id}", response_model=ClientResponse)
async def delete_customer(customer_id: str):
    deleted = await customer_collection.find_one_and_delete({"_id": ObjectId(customer_id)})
    if not deleted:
        raise HTTPException(status_code=404, detail="Customer not found")

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
