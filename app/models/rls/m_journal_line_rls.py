import uuid
from typing import List, Optional, Dict, Any
from datetime import datetime

from sqlmodel import Column, SQLModel, Field
from sqlalchemy.dialects.postgresql import JSONB

from app.models.m_mixin import BaseMixin


# --- Journal Line Base ---
class JournalLineBase(SQLModel):
    account_id: str = Field(index=True)
    debit: float = 0.0
    credit: float = 0.0
    extras: Dict[str, Any] = Field(default_factory=dict, sa_column=Column(JSONB))


# --- Journal Line DB Table ---
class JournalLineDB(JournalLineBase, BaseMixin, table=True):
    __tablename__ = "journal_lines_rls"
    journal_header_id: uuid.UUID = Field(foreign_key="journal_headers_rls.id", index=True)
    # No Relationship needed


# --- Pydantic / API Models ---
class JournalLineCreate(JournalLineBase):
    journal_header_id: Optional[uuid.UUID] = None
    

class JournalLineRead(JournalLineBase):
    id: uuid.UUID
    journal_header_id: uuid.UUID
    # journal: Optional["JournalRead"] removed
