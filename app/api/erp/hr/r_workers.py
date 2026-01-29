from typing import Any, Dict, List
from fastapi import APIRouter, Body, HTTPException
from bson import ObjectId
from pymongo import ReturnDocument

from app.models.m_worker import WorkerCreate, Worker
from app.db.x_mg_conn import workers_collection, dynamic_collection
from app.utils.u_sequence import get_next_sequence
from datetime import datetime, date

router = APIRouter()

def convert_dates(document: dict):
    """Converts all date fields to datetime for MongoDB compatibility"""
    for key, value in document.items():
        if isinstance(value, date) and not isinstance(value, datetime):
            document[key] = datetime.combine(value, datetime.min.time())
    return document



@router.post("/dynamic_workers", response_model=Dict[str, Any], status_code=201)
async def create_dynamic_worker(data: Dict[str, Any] = Body(...)):
    data = convert_dates(data)
    data["is_active"] = True
    data["employee_id"] = await get_next_sequence("employee_id")
    result = await dynamic_collection.insert_one(data)

    data["id"] = str(result.inserted_id)
    data.pop("_id", None)  # ✅ Remove non-serializable ObjectId

    return data



@router.get("/dynamic_workers", response_model=List[Dict[str, Any]])
async def get_all_dynamic_workers():
    cursor = dynamic_collection.find()
    results = []
    async for doc in cursor:
        doc["id"] = str(doc["_id"])
        doc.pop("_id", None)  # ✅ This removes the problematic ObjectId
        results.append(doc)
    return results



@router.post("/workers", response_model=Worker, status_code=201)
async def create_worker(worker: WorkerCreate):
    # Ensure email uniqueness
    existing = await workers_collection.find_one({"email": worker.email})
    if existing:
        raise HTTPException(status_code=400, detail="Worker already exists")

    worker_dict = worker.model_dump()
    worker_dict = convert_dates(worker_dict)
    worker_dict["is_active"] = True

    result = await workers_collection.insert_one(worker_dict)
    return Worker(id=str(result.inserted_id), **worker_dict)



@router.get("/workers", response_model=list[Worker])
async def get_all_workers():
    workers = []
    async for doc in workers_collection.find():
        doc["id"] = str(doc["_id"])
        doc.pop("_id")
        workers.append(Worker(**doc))
    return workers


@router.get("/workers/{worker_id}", response_model=Worker)
async def get_worker(worker_id: str):
    try:
        obj_id = ObjectId(worker_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid worker ID format")

    worker = await workers_collection.find_one({"_id": obj_id})
    if not worker:
        raise HTTPException(status_code=404, detail="Worker not found")

    worker["id"] = str(worker["_id"])
    worker.pop("_id")
    return Worker(**worker)



@router.put("/workers/{worker_id}", response_model=Worker)
async def update_worker(worker_id: str, data: dict = Body(...)):
    try:
        obj_id = ObjectId(worker_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid worker ID")

    # Convert any date fields in update
    for key, value in data.items():
        if isinstance(value, date) and not isinstance(value, datetime):
            data[key] = datetime.combine(value, datetime.min.time())

    updated = await workers_collection.find_one_and_update(
        {"_id": obj_id},
        {"$set": data},
        return_document=ReturnDocument.AFTER
    )

    if not updated:
        raise HTTPException(status_code=404, detail="Worker not found")

    updated["id"] = str(updated["_id"])
    updated.pop("_id")
    return Worker(**updated)


@router.delete("/workers/{worker_id}", status_code=204)
async def delete_worker(worker_id: str):
    try:
        obj_id = ObjectId(worker_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid worker ID")

    result = await workers_collection.delete_one({"_id": obj_id})

    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Worker not found")

    return




@router.get("/dynamic_workers/{employee_id}", response_model=Dict[str, Any])
async def get_dynamic_worker(employee_id: int):
    doc = await dynamic_collection.find_one({"employee_id": employee_id})
    if not doc:
        raise HTTPException(status_code=404, detail="Worker not found")
    
    doc["id"] = str(doc["_id"])
    doc.pop("_id", None)  # ✅ Remove ObjectId before returning
    return doc
