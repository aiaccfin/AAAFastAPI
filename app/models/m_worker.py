from pydantic import BaseModel, EmailStr, Field
from typing import Optional, Literal
from datetime import date

class WorkerBase(BaseModel):
    legal_name: str
    preferred_name: Optional[str] = None

    email: EmailStr
    phone: Optional[str] = None

    sin: Optional[str] = None  # Canadian
    ssn: Optional[str] = None  # US

    date_of_birth: Optional[date] = None
    nationality: Optional[str] = None

    address: Optional[str] = None
    city: Optional[str] = None
    province_or_state: Optional[str] = None
    country: Optional[str] = None
    postal_code: Optional[str] = None

    employment_type: Literal["employee", "contractor"]
    work_authorization: Optional[str] = None
    position_title: Optional[str] = None
    department: Optional[str] = None
    hire_date: Optional[date] = None

class WorkerCreate(WorkerBase):
    pass

class Worker(WorkerBase):
    id: str
    is_active: bool
