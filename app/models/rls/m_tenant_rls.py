from sqlmodel import SQLModel, Field, Relationship
from typing import List, Optional, Dict, Any
from datetime import datetime
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy import Column, Text, CheckConstraint, text
from sqlalchemy.orm import sessionmaker
import uuid

# Tenant model for RLS
class Tenant(SQLModel, table=True):
    __tablename__ = "tenants"
    
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)

    name: str = Field(index=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    created_by: Optional[str] = Field(default="admin")

    is_active: bool = Field(default=True)
    notes: Dict[str, Any] = Field(
        default=dict, sa_column=Column(JSONB))  # 备注和自定义字段
