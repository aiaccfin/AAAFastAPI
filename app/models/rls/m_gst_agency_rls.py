import uuid
from typing import List, Optional, Dict, Any
from sqlmodel import Relationship, SQLModel, Field, Column
from sqlalchemy.dialects.postgresql import JSONB
from app.models.m_mixin import BaseMixin


class TaxAgencyBase(SQLModel):
    name: str
    description: Optional[str] = None
    gst_hst_number: Optional[str] = None
    filing_frequency: Optional[str] = None
    reporting_method: Optional[str] = None
    start_of_tax_period: Optional[str] = None
    extras: Dict[str, Any] = Field(
        default_factory=dict,  # use factory, not default={}
        sa_column=Column(JSONB)  # PostgreSQL JSONB column
    )


class TaxAgency(TaxAgencyBase, BaseMixin, table=True):
    __tablename__ = "tax_agency_rls"


class TaxAgencyCreate(TaxAgencyBase):
    pass


class TaxAgencyRead(TaxAgencyBase):
    id: uuid.UUID
    extras: Optional[dict] = None
    
    
class TaxAgencyUpdate(SQLModel):
    name: Optional[str] = None
    description: Optional[str] = None
    gst_hst_number: Optional[str] = None
    filing_frequency: Optional[str] = None
    reporting_method: Optional[str] = None
    start_of_tax_period: Optional[str] = None
    extras: Optional[Dict[str, Any]] = None