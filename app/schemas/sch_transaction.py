from datetime import datetime
from typing import Optional, List
from uuid import UUID

from pydantic import BaseModel, Field


# =========================
# Base
# =========================

class TransactionBase(BaseModel):
    tenant_id: UUID = "550e8400-e29b-41d4-a716-446655440000"

    amount: float
    currency: str = "USD"
    type: str = "transaction"
    from_account: str = "from"
    to_account: str = "to"

    from_accounts: Optional[List[str]] = None
    to_accounts: Optional[List[str]] = None
    from_biz:Optional[dict] = None
    to_biz:Optional[dict] = None
    
    from_bk1: Optional[List[dict]] = None
    to_bk1: Optional[List[dict]] = None
    from_bk2: Optional[List[dict]] = None
    to_bk2: Optional[List[dict]] = None

    # from_undeposited_payments: Optional[List[dict]] = None
    # from_additional_funds: Optional[List[dict]] = None
    # to_accounts_j: Optional[List[dict]] = None

    
    memo: Optional[dict] = None
    reference: Optional[str] = None

    is_flagged: bool = False
    date_time: Optional[datetime] = None

    tags: Optional[List[str]] = None


# =========================
# Create
# =========================

class TransactionCreate(TransactionBase):
    pass


# =========================
# Update
# =========================

class TransactionUpdate(BaseModel):
    amount: Optional[float] = None
    currency: Optional[str] = None
    type: Optional[str] = None
    from_account: Optional[str] = None
    to_account: Optional[str] = None
    
    from_accounts: Optional[List[str]] = None
    to_accounts: Optional[List[str]] = None
    date_time: Optional[datetime] = None
    from_biz:Optional[dict] = None
    to_biz:Optional[dict] = None
    
    from_bk1: Optional[List[dict]] = None   # ARRAY(JSONB)
    to_bk1: Optional[List[dict]] = None     # ARRAY(JSONB)
    from_bk2: List[dict] = Field(default_factory=list)  # JSONB, required
    to_bk2: List[dict] = Field(default_factory=list)    # JSONB, required


    # from_undeposited_payments: Optional[List[dict]] = None
    # from_additional_funds: Optional[List[dict]] = None
    # to_accounts_j: Optional[List[dict]] = None

    memo: Optional[dict] = None
    reference: Optional[str] = None

    is_flagged: Optional[bool] = None
    tags: Optional[List[str]] = None


# =========================
# Read
# =========================

class TransactionRead(TransactionBase):
    id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
