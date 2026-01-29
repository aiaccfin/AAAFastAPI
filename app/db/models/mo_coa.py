from sqlalchemy import Column, ForeignKey, String, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from typing import Optional, List, Dict, Any
import uuid

from .mo_base import Base, BaseMixin, TenantMixin


class COABase(BaseMixin):
    __abstract__ = True  # not a table by itself

    code: Mapped[str] = mapped_column(String, index=True)
    name: Mapped[str] = mapped_column(String)
    type: Mapped[str] = mapped_column(String)
    detail_type: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    currency: Mapped[Optional[str]] = mapped_column(String, nullable=True)

    # JSON columns
    posting: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    extras: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)


class COADB(TenantMixin, COABase, Base):
    __tablename__ = "coa_rls"

    parent_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("coa_rls.id", ondelete="SET NULL"),
        nullable=True,
        index=True
    )

    # Self-referential relationships
    children: Mapped[List["COADB"]] = relationship(
        "COADB",
        back_populates="parent",
        cascade="all, delete-orphan"
    )

    parent: Mapped[Optional["COADB"]] = relationship(
        "COADB",
        back_populates="children",
        remote_side="COADB.id"
    )
