from sqlmodel import Field, SQLModel
from sqlalchemy import Column
from sqlalchemy.dialects.postgresql import JSONB

from typing import Any, Dict, Optional

from pydantic import BaseModel, EmailStr, Field, field_validator, validator

from app.db.model_base import AllBase

class Biz_User(AllBase, table=True):
    username:        Optional[str] = Field(default=None, index=True, unique=True)
    email:           Optional[str] = Field(default=None, index=True, unique=True)
    password_hashed : Optional[str]
    primary_group_id:Optional[int]
    primary_role_id :Optional[int]


class UserCreate(BaseModel):
    biz_id: int
    username: str
    email: EmailStr
    password: str = Field(..., min_length=6)
    primary_group_id: int
    primary_role_id: int

    @field_validator("username")
    def no_whitespace(cls, value):
        if " " in value:
            raise ValueError("username cannot contain spaces")
        return value
