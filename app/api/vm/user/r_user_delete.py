from fastapi import APIRouter, HTTPException
from app.models.m_user import UserEmail  # reuse same model
from app.db.x_mg_conn import users_collection,verification_collection

router = APIRouter()

@router.delete("/delete-user", status_code=200)
async def delete_user_by_email(user: UserEmail):
    result1 = await verification_collection.delete_one({"email": user.email})
    result = await users_collection.delete_one({"email": user.email})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="User not found")
    return {"detail": f"User with email '{user.email}' deleted"}
