from typing import List
from fastapi import APIRouter,Depends

from app.models.m_user import RoleCreate, Role
from app.db.x_mg_conn import roles_collection

router = APIRouter()

@router.post("/", response_model=Role)
async def create_role(role: RoleCreate):
    role_dict = role.model_dump()
    result = await roles_collection.insert_one(role_dict)  # Use `await`
    return Role(id=str(result.inserted_id), **role_dict)

@router.get("/", response_model=List[Role])
async def get_roles():
    roles = await roles_collection.find().to_list(None)  # Fetch all roles

    # Convert ObjectId to string and remove _id
    for role in roles:
        role["id"] = str(role["_id"])  # Convert ObjectId to string
        del role["_id"]  # Remove _id if not needed

    return [Role(**role) for role in roles]

