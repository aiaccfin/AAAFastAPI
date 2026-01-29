from typing import Any, Dict
from fastapi import APIRouter, Body, HTTPException
from bson import ObjectId
from datetime import datetime, date

from app.db.x_mg_conn import product_collection
from app.utils.u_sequence import get_next_sequence

router = APIRouter()


def convert_dates(document: dict):
    """Converts all date fields to datetime for MongoDB compatibility"""
    for key, value in document.items():
        if isinstance(value, date) and not isinstance(value, datetime):
            document[key] = datetime.combine(value, datetime.min.time())
    return document


# -----------------------------
# Create Product
# -----------------------------
@router.post("/products", response_model=Dict[str, Any], status_code=201)
async def create_product(
    data: Dict[str, Any] = Body(
        ...,
        example = {
            "name": "Laptop",
            "description": "High performance laptop",
            "sku": "LAP-001",
            "category": "Electronics",
            "brand": "BrandName",
            "pricing": {
                "price": 1200.00,
                "currency": "CAD"
            },
            "stock": {
                "quantity": 10,
                "reorder_level": 2
            },
            "dates": {
                "manufacture_date": "2025-01-01",
                "expiry_date": None
            },
            "attributes": {
                "color": "Silver",
                "weight_kg": 1.5,
                "warranty_years": 2
            }
        }
    )
):
    data = convert_dates(data)
    data["is_active"] = True
    data["product_id"] = await get_next_sequence("product_id")

    result = await product_collection.insert_one(data)
    data["id"] = str(result.inserted_id)
    data.pop("_id", None)

    return data


# -----------------------------
# Read/Get Product by ID
# -----------------------------
@router.get("/products/{product_id}", response_model=Dict[str, Any])
async def get_product(product_id: str):
    product = await product_collection.find_one({"_id": ObjectId(product_id)})
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    product["id"] = str(product["_id"])
    product.pop("_id", None)
    return product


# -----------------------------
# Update Product by ID
# -----------------------------
@router.put("/products/{product_id}", response_model=Dict[str, Any])
async def update_product(product_id: str, data: Dict[str, Any] = Body(...)):
    data = convert_dates(data)
    updated = await product_collection.find_one_and_update(
        {"_id": ObjectId(product_id)},
        {"$set": data},
        return_document=True
    )

    if not updated:
        raise HTTPException(status_code=404, detail="Product not found")

    updated["id"] = str(updated["_id"])
    updated.pop("_id", None)
    return updated


# -----------------------------
# Delete Product by ID
# -----------------------------
@router.delete("/products/{product_id}", response_model=Dict[str, Any])
async def delete_product(product_id: str):
    deleted = await product_collection.find_one_and_delete({"_id": ObjectId(product_id)})
    if not deleted:
        raise HTTPException(status_code=404, detail="Product not found")

    deleted["id"] = str(deleted["_id"])
    deleted.pop("_id", None)
    return deleted


# -----------------------------
# List all products
# -----------------------------
@router.get("/products", response_model=Dict[str, Any])
async def list_products():
    cursor = product_collection.find()
    products = []
    async for doc in cursor:
        doc["id"] = str(doc["_id"])
        doc.pop("_id", None)
        products.append(doc)
    return {"products": products}
