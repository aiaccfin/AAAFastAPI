from sqlmodel import Field, SQLModel
from sqlalchemy import Column
from sqlalchemy.dialects.postgresql import JSONB

from typing import Any, Dict, Optional

from app.db.model_base import AllBase

class BizBase(SQLModel):
   id: Optional[int] = Field(default=None, primary_key=True)  # Auto-increment ID
   biz_name: str
   biz_city: Optional[str]
   biz_county: Optional[str]
   biz_state: Optional[str]
   biz_province: Optional[str]
   biz_country: Optional[str]
   biz_info: Optional[Dict[str, Any]] = Field(default=None, sa_column=Column(JSONB))
   biz_recon_tolerance: Optional[int]
   biz_industry_id:  Optional[int]
   biz_industry: Optional[str]
   biz_base_currency: Optional[str]
   biz_fiscal_year: Optional[str]
   biz_tax_setting: Optional[str]
   biz_default_payment_term: Optional[str]
   biz_integration_setting: Optional[str]
   biz_primary_bank_id: Optional[int]
   biz_accounting_method: Optional[str]
   biz_bk1: Optional[str]
   biz_bk2: Optional[str]
   biz_bk3: Optional[str]
   biz_bk4: Optional[str]
   status: Optional[str]
   note: Optional[str]


class Biz_Entity(BizBase, table=True):  # Table for database
    pass


class BizEntityCreate(BizBase):  # Used for request body
    pass


class BizEntityRead(BizBase):  # Used for response models
    pass


class BizEntityUpdate(SQLModel):  # Used for partial updates
    pass
