# app/models/acc/journal.py
import uuid
from datetime import datetime
from typing import List, Optional

from sqlalchemy import String, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .mo_base import Base, BaseMixin, TenantMixin
from .mo_journal_line import JournalLineDB


class JournalEntryDB(TenantMixin, BaseMixin, Base):
    __tablename__ = "journal_entries"

    source_type: Mapped[str] = mapped_column(String, index=True)   # "invoice"
    source_id: Mapped[uuid.UUID] = mapped_column(PG_UUID(as_uuid=True), index=True)

    entry_date: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow
    )

    memo: Mapped[Optional[str]] = mapped_column(String, nullable=True)

    lines: Mapped[List["JournalLineDB"]] = relationship(
        "JournalLineDB",
        back_populates="entry",
        cascade="all, delete-orphan"
    )
