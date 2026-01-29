import uuid
from typing import List, Optional, Dict, Any
from datetime import datetime

from sqlmodel import Column, SQLModel, Field
from sqlalchemy.dialects.postgresql import JSONB

from app.models.m_mixin import BaseMixin
from app.models.rls.m_journal_line_rls import JournalLineCreate, JournalLineRead


# --- Journal Base (common fields) ---
class JournalHeaderBase(SQLModel):
    
    reference: Optional[str] = Field(default=None, index=True)
    memo: Optional[str] = None
    posted_at: Optional[datetime] = None
    extras: Dict[str, Any] = Field(default_factory=dict, sa_column=Column(JSONB))


# --- Journal DB Table ---
class JournalHeaderDB(JournalHeaderBase, BaseMixin, table=True):
    __tablename__ = "journal_headers_rls"
    # No Relationship; DB stays the same


# --- Pydantic / API Models ---
class JournalHeaderCreate(JournalHeaderBase):
    journal_lines: Optional[List["JournalLineCreate"]] = Field(default_factory=list)

class JournalHeaderRead(JournalHeaderBase):
    id: uuid.UUID
    journal_lines: Optional[List["JournalLineRead"]] = Field(default_factory=list)
