# app/models/acc/journal_line.py
import uuid
from typing import Optional

from sqlalchemy import ForeignKey
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.models.mo_journal_header import JournalEntryDB

from .mo_base import Base, BaseMixin, TenantMixin


class JournalLineDB(Base):
    __tablename__ = "journal_lines"

    entry_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("journal_entries.id", ondelete="CASCADE"),
        index=True
    )

    coa_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("coa_rls.id"),
        index=True
    )

    debit: Mapped[float] = mapped_column(default=0)
    credit: Mapped[float] = mapped_column(default=0)

    entry: Mapped[Optional["JournalEntryDB"]] = relationship(
        "JournalEntryDB",
        back_populates="lines"
    )
