# app/models/rls/m_bill_payment_rls.py
import uuid
from typing import List, Optional, Dict, Any
from datetime import datetime

from sqlmodel import Relationship, SQLModel, Field, Column
from sqlalchemy.dialects.postgresql import JSONB

from app.models.m_mixin import BaseMixin
from app.models.rls.m_journal_line_rls import JournalLineCreate
from app.models.rls.m_bill_payment_allocation_rls import BillPaymentAllocationCreate
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.models.rls.m_bill_payment_allocation_rls import BillPaymentAllocationDB

class BillPaymentBase(SQLModel):
    amount: float = 0.0
    payment_date: datetime = Field(default_factory=datetime.utcnow)

    # Existing
    extras: Dict[str, Any] = Field(
        default_factory=dict,
        sa_column=Column(JSONB)
    )

    payee_id: Optional[uuid.UUID] = Field(default_factory=uuid.uuid4, index=True)
    payee_snapshot: Optional[Dict[str, Any]] = Field(
        default=None,
        sa_column=Column(JSONB)
    )
    payment_method: Optional[str] = "Cash"
    deposit_account_id: Optional[uuid.UUID] = None
    reference_no: Optional[str] = "no reference number"
    notes: Dict[str, Any] = Field(
        default_factory=dict,
        sa_column=Column(JSONB)
    )
    amount_paid: Optional[float] = 0.0


class BillPaymentDB(BillPaymentBase, BaseMixin, table=True):
    __tablename__ = "bill_payments_rls"
    reference_id: Optional[uuid.UUID] = Field(default=None, index=True)  # link to referenceDB.id (optional)
    bill_payment_allocations: List["BillPaymentAllocationDB"] = Relationship(
        sa_relationship_kwargs={
            "primaryjoin": "and_(BillPaymentDB.id == BillPaymentAllocationDB.source_id, BillPaymentAllocationDB.source_type == 'payment')",
            "foreign_keys": "[BillPaymentAllocationDB.source_id]",
            "viewonly": True
        }
    )
    


class BillPaymentCreate(BillPaymentBase):
    reference_id: Optional[uuid.UUID] = None


class BillPaymentRead(BillPaymentBase):
    id: uuid.UUID
    reference_id: Optional[uuid.UUID]
    created_at: datetime
    created_by: str
    status: str = "active"


class BillPaymentUpdate(SQLModel):
    amount: Optional[float] = None
    payment_date: Optional[datetime] = None

    extras: Optional[Dict[str, Any]] = None

    payee_id: Optional[uuid.UUID] = None
    payee_snapshot: Optional[Dict[str, Any]] = None

    payment_method: Optional[str] = None
    deposit_account_id: Optional[uuid.UUID] = None

    reference_no: Optional[str] = None
    notes: Optional[Dict[str, Any]] = None

    amount_paid: Optional[float] = None

    reference_id: Optional[uuid.UUID] = None


class BillPaymentDelete(SQLModel):
    is_deleted: bool = Field(default=True)


class BillPaymentVoid(SQLModel):
    journal_lines: Optional[List[JournalLineCreate]] = Field(default_factory=list)


class BillPaymentWithAllocationsCreate(SQLModel):
    """Request model for creating a bill payment with allocations"""
    # Payment fields
    amount: float = 0.0
    payment_date: Optional[datetime] = None
    payee_id: Optional[uuid.UUID] = None
    payee_snapshot: Optional[Dict[str, Any]] = None
    payment_method: Optional[str] = "Cash"
    deposit_account_id: Optional[uuid.UUID] = None
    reference_no: Optional[str] = "no reference number"
    notes: Optional[Dict[str, Any]] = None
    amount_paid: Optional[float] = 0.0
    reference_id: Optional[uuid.UUID] = None
    extras: Optional[Dict[str, Any]] = None
    
    # Allocations
    allocations: List[BillPaymentAllocationCreate]
    
    # Journal lines
    journal_lines: Optional[List[JournalLineCreate]] = Field(default_factory=list)