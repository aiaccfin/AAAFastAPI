from datetime import datetime, timezone
from typing import Any, Dict, Optional

from sqlalchemy import Column
from sqlalchemy.dialects.postgresql import JSONB

from sqlmodel import Field, SQLModel


class BizBankBase(SQLModel):
    id: Optional[int] = Field(default=None, primary_key=True)  # Auto-increment ID
    biz_id: int
    bank_account_number: Optional[str]
    bank_name: Optional[str]
    bank_code: Optional[str]
    bank_account_type: Optional[str]
    bank_info: Optional[Dict[str, Any]] = Field(default=None, sa_column=Column(JSONB))
    bk_acc_from_statement: Optional[str]
    status: Optional[str]
    note: Optional[str]  # Optional if the field allows NULL
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))  # Timestamp with timezone

class Biz_Bank(BizBankBase, table=True):  # Table for database
    pass


class BizBankCreate(BizBankBase):  # Used for request body
    pass

class BizBankRead(BizBankBase):  # Used for response models
    pass

class BizBankGet(BizBankBase):  # Used for response models
    pass

class BizBankUpdate(SQLModel):  # Used for partial updates
    id: Optional[int] = Field(default=None, primary_key=True)  # Auto-increment ID
    status: Optional[str]
    note: Optional[str]  
