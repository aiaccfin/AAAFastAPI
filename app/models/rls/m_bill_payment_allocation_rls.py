from typing import Optional, Literal
from sqlmodel import Relationship, SQLModel, Field
from sqlalchemy import Column, ForeignKey, CheckConstraint, String
from datetime import datetime
import uuid

from app.models.m_mixin import BaseMixin


from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.models.rls.m_bill_rls import BillDB


class BillPaymentAllocationBase(SQLModel):
    allocated_amount: float
    allocated_at: datetime = Field(default_factory=datetime.utcnow)


class BillPaymentAllocationDB(BillPaymentAllocationBase, BaseMixin, table=True):
    __tablename__ = "bill_payment_allocations_rls"
    __table_args__ = (
        # Ensure source_type is either "payment" or "credit"
        CheckConstraint(
            "source_type IN ('payment', 'credit')",
            name="check_source_type"
        ),
    )

    # Polymorphic source: merged from bill_payment_id and vendor_credit_id
    source_id: uuid.UUID = Field(
        nullable=False,
        index=True,
        description="ID of either bill_payment (if source_type='payment') or vendor_credit/bill (if source_type='credit')"
    )
    
    # Type discriminator: "payment" or "credit"
    source_type: Literal["payment", "credit"] = Field(
        default="payment",
        sa_column=Column(String(), nullable=False, server_default="payment", index=True),
        description="Type of source: 'payment' for bill payments, 'credit' for vendor credits"
    )
    
    # Foreign key to bill (the bill that receives the allocation)
    bill_id: uuid.UUID = Field(
        sa_column=Column(ForeignKey("bills_rls.id", ondelete="CASCADE"), nullable=False, index=True)
    )
    
    # Relationship to the bill that receives the allocation
    bill: "BillDB" = Relationship(
        sa_relationship_kwargs={
            "primaryjoin": "BillPaymentAllocationDB.bill_id == BillDB.id"
        }
    )

        

class BillPaymentAllocationCreate(BillPaymentAllocationBase):
    # source_id and source_type must be provided together
    source_id: uuid.UUID
    source_type: Literal["payment", "credit"]
    bill_id: uuid.UUID


class BillPaymentAllocationRead(BillPaymentAllocationBase):
    id: uuid.UUID
    source_id: uuid.UUID
    source_type: Literal["payment", "credit"]
    bill_id: uuid.UUID

