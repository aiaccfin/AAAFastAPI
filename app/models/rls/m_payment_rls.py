# app/models/rls/m_Payment_rls.py
import uuid
from typing import List, Optional, Dict, Any
from datetime import datetime

from sqlmodel import Relationship, SQLModel, Field, Column
from sqlalchemy.dialects.postgresql import JSONB

from app.models.m_mixin import BaseMixin, ReadMixin
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.models.rls.m_payment_allocation_rls import PaymentAllocationDB

class PaymentBase(SQLModel):
    amount: float = 0.0
    payment_date: datetime = Field(default_factory=datetime.utcnow)
    payment_type: Optional[str] = "Cash"
    payment_source: Optional[str] = "Reserved"

    # Existing
    extras: Dict[str, Any] = Field(
        default_factory=dict,
        sa_column=Column(JSONB)
    )

    customer_id: Optional[uuid.UUID] = Field(default_factory=uuid.uuid4,  index=True)
    customer_snapshot: Optional[Dict[str, Any]] = Field(
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
    amount_received: Optional[float] = 0.0
    amount1: Optional[float] = 0.0
    amount2: Optional[float] = 0.0
    amount3: Optional[float] = 0.0
    amount4: Optional[float] = 0.0


class PaymentDB(PaymentBase, BaseMixin, table=True):
    __tablename__ = "payments_rls"
    reference_id: Optional[uuid.UUID] = Field(default=None, index=True)  # link to referenceDB.id (optional)
    payment_allocations: List["PaymentAllocationDB"] = Relationship(back_populates="payment")
    


class PaymentCreate(PaymentBase):
    reference_id: Optional[uuid.UUID] = None


class PaymentRead(ReadMixin, PaymentBase):
    reference_id: Optional[uuid.UUID] = None
    status2: str = Field(default="second status")
    is_deleted: Optional[bool] 



class PaymentUpdate(SQLModel):
    id: uuid.UUID
    amount: Optional[float] = None
    payment_date: Optional[datetime] = None

    extras: Optional[Dict[str, Any]] = None

    customer_id: Optional[uuid.UUID] = None
    customer_snapshot: Optional[Dict[str, Any]] = None

    payment_method: Optional[str] = None
    deposit_account_id: Optional[uuid.UUID] = None

    reference_no: Optional[str] = None
    notes: Optional[Dict[str, Any]] = None

    amount_received: Optional[float] = None

    reference_id: Optional[uuid.UUID] = None
    is_deleted: Optional[bool] 



class PaymentAllocationRead(SQLModel):
    id: uuid.UUID
    payment_id: uuid.UUID
    invoice_id: uuid.UUID
    allocated_amount: float
    allocated_at: datetime
    is_deleted: Optional[bool] 
    
    
class PmtAllocRead(PaymentBase):
    id: uuid.UUID
    reference_id: Optional[uuid.UUID]
    payment_allocations: List[PaymentAllocationRead] = []
    is_deleted: Optional[bool] 
