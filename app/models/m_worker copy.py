from pydantic import BaseModel, Field, EmailStr
from typing import Optional
from datetime import date
from bson import ObjectId

class Address(BaseModel):
    street: str
    unit: Optional[str] = None
    city: str
    province: str
    postal_code: str
    country: str

class ManagerInfo(BaseModel):
    name: str
    title: Optional[str] = None
    email: Optional[EmailStr] = None


class WorkerCreate(BaseModel):
    legal_name: str
    preferred_name: Optional[str] = None
    email: EmailStr
    phone: str
    gender: Optional[str] = None
    date_of_birth: date

    identifier: str  # SIN/SSN
    country: str  # CA / US / etc.

    department: Optional[str] = None
    role: Optional[str] = None
    hire_date: Optional[date] = None
    location: Optional[str] = None

    manager: Optional[ManagerInfo] = None
    address: Optional[Address] = None


class Worker(WorkerCreate):
    id: str = Field(..., alias="_id")
    is_active: bool = True  # Based on the green "Active" badge

    class Config:
        populate_by_name = True
        json_encoders = {ObjectId: str}
