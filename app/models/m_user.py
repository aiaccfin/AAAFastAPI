from pydantic import BaseModel, EmailStr, Field
from typing import List, Optional


# Define TokenResponse model
class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    roles: list[str]
    groups: list[str]


class UserEmail(BaseModel):
    email: EmailStr


class UserCreate(BaseModel):
    email: EmailStr
    name: str
    password_hash: str
    roles: List[str] = Field(
        default=["88"]
    )  # Explicit default instead of default_factory
    groups: List[str] = Field(default=["9999"])
    primary_role: Optional[str] = "88"  # Fixed default: "88"
    primary_group: Optional[str] = "9999"  # Fixed default: "9999"
    email_verified: bool = False
    is_verified: bool = False


class EmailVerification(BaseModel):
    email: EmailStr
    code: str


class User(UserCreate):
    id: str


class RoleCreate(BaseModel):
    name: str
    description: Optional[str] = "module authorization"
    permissions: List[str] = []  # Example field, adjust as needed


class Role(RoleCreate):
    id: str  # MongoDB ObjectId as a string


class GroupCreate(BaseModel):
    name: str
    description: Optional[str] = "handle entities"
    biz_entities: List[str]  # List of Business Entity IDs


class Group(GroupCreate):
    id: str  # MongoDB _id


class LoginVerification(BaseModel):
    email: EmailStr
    code: str


class ResetPasswordConfirm(BaseModel):
    email: EmailStr
    code: str
    new_password: str
