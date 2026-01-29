from fastapi import APIRouter, HTTPException, Depends

from passlib.context import CryptContext # type: ignore

from app.models.m_user import UserCreate, User, TokenResponse, ResetPasswordConfirm, EmailVerification, UserEmail
from app.db.x_mg_conn import users_collection, verification_collection
from app.utils.gmail_api_sender import generate_and_send_verification_code

from passlib.context import CryptContext # type: ignore
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

router = APIRouter()


@router.post("/register", response_model=User,  status_code=201)
async def create_user(user: UserCreate):
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    user.password_hash = pwd_context.hash(user.password_hash)
    existing_user = await users_collection.find_one({"email": user.email})
    if existing_user:
        raise HTTPException(status_code=400, detail="User already exists")
    
    user_dict = user.model_dump()
    user_dict["is_verified"] = False
    
    new_user = await users_collection.insert_one(user_dict)
    await generate_and_send_verification_code(user.email)
    
    return {"id": str(new_user.inserted_id), **user_dict}



@router.post("/verify-email")
async def verify_email(data: EmailVerification):
    code_doc = await verification_collection.find_one({"email": data.email, "code": data.code})
    if not code_doc:
        raise HTTPException(status_code=400, detail="Invalid verification code")

    result = await users_collection.update_one(
        {"email": data.email},
        {"$set": {"is_verified": True}}
    )

    await verification_collection.delete_many({"email": data.email})
    return {"msg": "Email successfully verified"}


@router.post("/resend-verification")
async def resend_verification(data: EmailVerification):  # or use a simple `EmailRequest` model
    user = await users_collection.find_one({"email": data.email})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if user.get("is_verified"):
        raise HTTPException(status_code=400, detail="Email already verified")

    await generate_and_send_verification_code(data.email)
    return {"msg": "Verification code resent"}


@router.post("/reset-password/request")
async def request_password_reset(data: UserEmail):
    user = await users_collection.find_one({"email": data.email})
    # Always return success, do not reveal if user exists
    if user:
        await generate_and_send_verification_code(data.email)
    return {"msg": "If the email exists, a verification code has been sent."}

@router.post("/reset-password/confirm")
async def confirm_password_reset(data: ResetPasswordConfirm):
    code_doc = await verification_collection.find_one({"email": data.email, "code": data.code})
    if not code_doc:
        raise HTTPException(status_code=400, detail="Invalid or expired verification code")
    # Hash new password and update
    new_hash = pwd_context.hash(data.new_password)
    result = await users_collection.update_one(
        {"email": data.email},
        {"$set": {"password_hash": new_hash, "is_verified": True}},
    )
    await verification_collection.delete_many({"email": data.email})
    return {"msg": "Password reset successful"}