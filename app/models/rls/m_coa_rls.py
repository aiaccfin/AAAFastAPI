from typing import Optional, Dict, Any, List, TYPE_CHECKING
from sqlmodel import SQLModel, Field, Relationship, Column
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy import ForeignKey

import uuid
from datetime import datetime

# contains tenant_id, id, created_at, etc.
from app.models.rls.m_public_mixin import PublicMixin, TenantMixin

if TYPE_CHECKING:
    from app.models.rls.m_coa_rls import COADB


class COABase(PublicMixin):
    """
    Master chart of COAs with nested (hierarchical) support.
    """
    code: str = Field(index=True, description="Unique COA code")
    name: str = Field(description="COA name")
    type: str = Field(description="Asset, Liability, Equity, Revenue, Expense")
    detail_type: Optional[str] = Field(default=None, description="Sub-type of the COA")
    currency: Optional[str] = Field(default=None)
    
    posting: Optional[Dict[str, Any]] = Field(
        default_factory=dict,
        description="Allowed modules for posting",
        sa_column=Column(JSONB)
    )

    # Optional metadata
    extras: Optional[Dict[str, Any]] = Field(
        default_factory=dict, sa_column=Column(JSONB))


class COADB(TenantMixin, COABase,  table=True):
    __tablename__ = "coa_rls"

    # Self-referential hierarchy - using sa_column with ForeignKey for RLS tables
    parent_id: Optional[uuid.UUID] = Field(
        default=None,
        sa_column=Column(ForeignKey("coa_rls.id", ondelete="SET NULL"), nullable=True, index=True)
    )

    # ORM relationships for hierarchical navigation
    # For self-referential relationships, we need to set remote_side properly
    children: List["COADB"] = Relationship(back_populates="parent")
    parent: Optional["COADB"] = Relationship(
        back_populates="children",
        sa_relationship_kwargs={
            "primaryjoin": "COADB.parent_id == COADB.id",
            "remote_side": "COADB.id"
        }
    )


class COACreate(COABase):
    parent_id: Optional[uuid.UUID] = None


class COARead(COABase):
    id: uuid.UUID
    parent_id: Optional[uuid.UUID] = None