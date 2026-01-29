# app/models/generic.py
from sqlmodel import SQLModel, Field

from typing import ClassVar, Optional, Dict, Any, List, Sequence
from datetime import datetime
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy import Sequence, Integer, Column
import uuid

class GenericBase(SQLModel):
    key: str = Field(index=True, unique=True)  # Unique key for each data
    value: Dict[str, Any] = Field(
        default={}, sa_column=Column(JSONB))  
    description: Optional[str] = Field(default=None)  # Optional description

class GenericStore(GenericBase, table=True):
    __tablename__ = "generic_store"
    tenant_id: uuid.UUID = Field(index=True)           # RLS tenant field
    id: Optional[uuid.UUID] = Field(default_factory=uuid.uuid4, primary_key=True)
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    created_by: Optional[str] = Field(default=None)

class GenericCreate(GenericBase):
    pass

class GenericRead(GenericBase):
    id: uuid.UUID  # 🔥 改为 UUID
    key: str
    value: Dict[str, Any]
    description: Optional[str]


class GenericUpdate(SQLModel):
    key: Optional[str] = None
    value: Optional[Dict[str, Any]] = None
    description: Optional[str] = None