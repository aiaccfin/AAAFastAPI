# app/models/rls/m_bankstatement_rls.py
from typing import Optional
from sqlmodel import SQLModel, Field, Column
from sqlalchemy.dialects.postgresql import JSONB
from datetime import datetime
import uuid

class BankstatementBase(SQLModel):
    category: str = Field(index=True, default="customer type")         # e.g. "payment", "invoice_status"
    date: datetime
    amount: float
    type: str  # e.g. "credit", "debit"
    balance: float
    description: Optional[str] = Field(default=None)  # Optional description


class BankstatementDB(BankstatementBase, table=True):
    __tablename__ = "bankstatements_rls"
    tenant_id: uuid.UUID = Field(index=True)  # RLS / multi-tenant
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    

    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    created_by: Optional[str] = Field(default="aiagent")
    updated_by: Optional[str] = Field(default="mcp")
    
    
class BankstatementCreate(BankstatementBase):
    pass


class BankstatementRead(BankstatementBase):
    id: uuid.UUID  # 🔥 改为 UUID

