# models/partner.py
from sqlmodel import SQLModel, Field
from typing import Optional, Dict, Any, List
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy import Column
from enum import Enum
from datetime import datetime
import uuid

class PartnerType(str, Enum):
    CUSTOMER = "customer"
    VENDOR = "vendor"

class PartnerBase(SQLModel):
    type: PartnerType
    status: str = "active"
    partner_type: Optional[str] = "self defined"
    
    # Common fields from PDF
    company_name: Optional[str] = None
    display_name: str
    email: Optional[str] = None
    phone: Optional[str] = None
    mobile: Optional[str] = None
    fax: Optional[str] = None
    website: Optional[str] = None
    
    # Customer specific common fields
    customer_full_name: Optional[str] = None
    is_vip: bool = False
    open_balance: float = 0.0
    available_credit: float = 0.0
   
    
    # JSONB fields for complex data
    billing_address: Optional[Dict[str, Any]] = Field(default=None, sa_column=Column(JSONB))
    shipping_address: Optional[Dict[str, Any]] = Field(default=None, sa_column=Column(JSONB))
    same_as_billing_address: bool = True
    payments: Optional[Dict[str, Any]] = Field(default=None, sa_column=Column(JSONB))
    bank_details: Optional[Dict[str, Any]] = Field(default=None, sa_column=Column(JSONB))
    contactors: List[Dict[str, Any]] = Field(default=[], sa_column=Column(JSONB))
    notes: List[Dict[str, Any]] = Field(default=[], sa_column=Column(JSONB))
    attachments: List[Dict[str, Any]] = Field(default=[], sa_column=Column(JSONB))
    transactions: List[Dict[str, Any]] = Field(default=[], sa_column=Column(JSONB))

class Partner(PartnerBase, table=True):
    __tablename__ = "partners"
    tenant_id: uuid.UUID = Field(index=True)           # RLS tenant field
    
    id: Optional[uuid.UUID] = Field(default_factory=uuid.uuid4, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

# Request/Response Models
class PartnerCreate(PartnerBase):
    pass

class PartnerUpdate(SQLModel):
    status: Optional[str] = None
    company_name: Optional[str] = None
    display_name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    mobile: Optional[str] = None
    fax: Optional[str] = None
    website: Optional[str] = None
    customer_full_name: Optional[str] = None
    is_vip: Optional[bool] = None
    open_balance: Optional[float] = None
    available_credit: Optional[float] = None
    billing_address: Optional[Dict[str, Any]] = None
    shipping_address: Optional[Dict[str, Any]] = None
    same_as_billing_address: Optional[bool] = None
    payments: Optional[Dict[str, Any]] = None
    bank_details: Optional[Dict[str, Any]] = None
    contactors: Optional[List[Dict[str, Any]]] = None

class PartnerResponse(PartnerBase):
    id: uuid.UUID
    created_at: datetime
    updated_at: datetime

class PartnerBrief(SQLModel):
    id: uuid.UUID
    type: PartnerType
    company_name: Optional[str] = None
    display_name: str
    status: str
    email: Optional[str] = None
    phone: Optional[str] = None
    open_balance: float = 0.0
    available_credit: float = 0.0
    customer_full_name: Optional[str] = None
