from typing import Optional, Dict, Any, List
from pydantic import BaseModel
from uuid import UUID
from decimal import Decimal
from datetime import datetime


# Base schema: shared fields
class COABaseSchema(BaseModel):
    code: str
    name: str
    type: str
    detail_type: Optional[str] = None
    currency: Optional[str] = None
    posting: Optional[Dict[str, Any]] = {}
    extras: Optional[Dict[str, Any]] = {}
    date_time: Optional[datetime] = None

    class Config:
        orm_mode = True  # allows from_orm


# Create schema: used for input when creating
class COACreateSchema(COABaseSchema):
    parent_id: Optional[UUID] = None


# Read schema: used for output / response
class COAReadSchema(COABaseSchema):
    id: UUID
    parent_id: Optional[UUID] = None
    children: Optional[List["COAReadSchema"]] = []  # recursive children

    # Optional audit fields from BaseMixin (if you want to expose)
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    deleted_at: Optional[datetime] = None
    created_by: Optional[str] = None
    updated_by: Optional[str] = None
    deleted_by: Optional[str] = None
    version: Optional[int] = None
    status: Optional[str] = None
    description: Optional[str] = None
    is_deleted: Optional[bool] = None

    class Config:
        orm_mode = True


# For recursive models, Pydantic requires this
COAReadSchema.update_forward_refs()
