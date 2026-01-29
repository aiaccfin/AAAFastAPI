from typing import List
from fastapi import APIRouter, Depends

from app.models.m_user import GroupCreate, Group
from app.db.x_mg_conn import groups_collection

router = APIRouter()

@router.post("/", response_model=Group, status_code=201)
async def create_group(group: GroupCreate):
    group_dict = group.model_dump()
    result = await groups_collection.insert_one(group_dict)  # Use `await`
    return Group(id=str(result.inserted_id), **group_dict)

@router.get("/", response_model=List[Group])
async def get_groups():
    groups = await groups_collection.find().to_list(None)  # Fetch all roles

    for group in groups:
        group["id"] = str(group["_id"])  # Convert ObjectId to string
        del group["_id"]  # Remove _id if not needed

    return [Group(**group) for group in groups]

