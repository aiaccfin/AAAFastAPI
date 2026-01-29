import uuid
from sqlmodel import SQLModel, Field
from typing import Optional, Dict, Any
from datetime import datetime
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy import Column
from pydantic import BaseModel

# -----------------------------
# Table / DB model
# -----------------------------
class GSTBase(SQLModel):
    tax_code: str = Field(index=True)            # e.g., "GST", "PST", "HST"
    tax_name: str                                 # e.g., "Goods and Services Tax"
    tax_rate: float = Field(ge=0, le=10000)          # 0.05 = 5%
    is_active: bool = Field(default=True)
    effective_date: datetime
    
    # Flexible JSONB fields
    tax_data: Dict[str, Any] = Field(default={}, sa_column=Column(JSONB))
    jurisdiction_data: Dict[str, Any] = Field(default={}, sa_column=Column(JSONB))
    compliance_data: Dict[str, Any] = Field(default={}, sa_column=Column(JSONB))


class GSTTable(GSTBase, table=True):
    __tablename__ = "gst62_rls"

    tenant_id: uuid.UUID = Field(index=True)           # RLS tenant field
    id: Optional[uuid.UUID] = Field(default_factory=uuid.uuid4, primary_key=True)
    
    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    created_by: Optional[str] = Field(default=None)


# -----------------------------
# Request / Response Models
# -----------------------------
class GSTCreate(GSTBase):
    """Input model for creating a GST record"""
    pass


class GSTRead(GSTBase):
    """Output model for reading a GST record"""
    id: uuid.UUID
    created_at: datetime
    updated_at: datetime


class GSTUpdateRequest(BaseModel):
    """Input model for updating a GST record dynamically"""
    tax_code: str           # Identify the record
    field_name: str         # Field to update
    new_value: Any          # New value


