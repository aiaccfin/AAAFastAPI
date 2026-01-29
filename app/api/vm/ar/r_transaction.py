from typing import List
from fastapi import APIRouter, HTTPException
from datetime import datetime

from pydantic import BaseModel, Field

# Import Transaction schema (you’ll need to define this similar to InvoiceItem)
from app.schemas.s_transaction import Transaction  
from app.db.x_mg_conn import transaction_collection  # new MongoDB collection for transactions

router = APIRouter()


# ----------- CREATE TRANSACTION (payment) -----------
@router.post("/", response_model=Transaction)
async def create_transaction(transaction: Transaction):
    transaction_data = transaction.dict()
    transaction_data["created_at"] = datetime.utcnow()

    result = await transaction_collection.insert_one(transaction_data)
    if not result.inserted_id:
        raise HTTPException(status_code=500, detail="Transaction could not be created")

    transaction_data["_id"] = str(result.inserted_id)
    return transaction_data


# ----------- GET ALL TRANSACTIONS -----------
@router.get("/", response_model=List[Transaction])
async def get_transactions():
    transactions = await transaction_collection.find().to_list(100)

    # convert MongoDB ObjectId to string
    for trx in transactions:
        if "_id" in trx:
            trx["_id"] = str(trx["_id"])

    return transactions


# ----------- GET SINGLE TRANSACTION -----------
@router.get("/{transaction_id}", response_model=Transaction)
async def get_transaction(transaction_id: str):
    trx = await transaction_collection.find_one({"transaction_id": transaction_id})
    if not trx:
        raise HTTPException(status_code=404, detail="Transaction not found")

    if "_id" in trx:
        trx["_id"] = str(trx["_id"])

    return trx


# ----------- UPDATE TRANSACTION -----------
@router.put("/{transaction_id}", response_model=Transaction)
async def update_transaction(transaction_id: str, transaction: Transaction):
    update_data = transaction.dict(exclude_unset=True)
    update_data["updated_at"] = datetime.utcnow()

    result = await transaction_collection.update_one(
        {"transaction_id": transaction_id}, {"$set": update_data}
    )

    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Transaction not found")

    updated_trx = await transaction_collection.find_one({"transaction_id": transaction_id})
    if "_id" in updated_trx:
        updated_trx["_id"] = str(updated_trx["_id"])

    return updated_trx


# ----------- DELETE TRANSACTION (Hard Delete) -----------
@router.delete("/{transaction_id}")
async def delete_transaction(transaction_id: str):
    result = await transaction_collection.delete_one({"transaction_id": transaction_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Transaction not found")
    return {"detail": "Transaction deleted successfully"}
