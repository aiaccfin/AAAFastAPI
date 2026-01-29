from typing import List, Optional
from uuid import UUID
from datetime import datetime
from pydantic import BaseModel


# -----------------------------
#   JOURNAL LINE
# -----------------------------
class JournalLineCreate(BaseModel):
    account_id: str
    debit: float = 0.0
    credit: float = 0.0
    extras: dict = {}


class JournalLineOut(BaseModel):
    id: UUID
    journal_id: UUID
    account_id: str
    debit: float
    credit: float
    extras: dict
    created_at: Optional[datetime]
    updated_at: Optional[datetime]
    tenant_id: UUID
    created_by: Optional[str]


# -----------------------------
#   JOURNAL HEADER
# -----------------------------
class JournalCreate(BaseModel):
    reference: Optional[str] = None
    memo: Optional[str] = None
    posted_at: Optional[datetime] = None
    extras: dict = {}
    journal_lines: List[JournalLineCreate] = []


class JournalOut(BaseModel):
    id: UUID
    reference: Optional[str]
    memo: Optional[str]
    posted_at: Optional[datetime]
    extras: dict
    journal_lines: List[JournalLineOut]
    tenant_id: UUID
    created_at: datetime
    updated_at: datetime
    created_by: Optional[str]
