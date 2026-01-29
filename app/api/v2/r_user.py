from typing  import Optional, List
from fastapi import APIRouter, Depends
from app.db  import db_asyncpg_user
from app.schemas.user_schema import User

router = APIRouter()

@router.get("/")
async def get_all_users(limit: Optional[int] = 10, offset: Optional[int] = 0):
    return await db_asyncpg_user.get_all_users(limit, offset)

@router.get("/{email}")
async def get_user_by_email(email: str):
    return await db_asyncpg_user.get_user_by_email(email)

@router.post("/")
async def insert_user(user: User):
    return await db_asyncpg_user.insert_user(user)

@router.post("/bulk")
async def bulk_insert_users(users: List[User]):
    return await db_asyncpg_user.bulk_insert_users(users)