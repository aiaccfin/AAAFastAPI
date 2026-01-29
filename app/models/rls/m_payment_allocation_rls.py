from typing import Optional
from sqlmodel import Relationship, SQLModel, Field
from sqlalchemy import Column, ForeignKey
from datetime import datetime
import uuid

from app.models.m_mixin import BaseMixin
from app.models.rls.m_payment_rls import PaymentDB


from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.models.rls.m_invoice_rls import InvoiceDB


class PaymentAllocationBase(SQLModel):
    allocated_amount: float
    allocated_at: datetime = Field(default_factory=datetime.utcnow)
    version: Optional[int] = Field(default=1)
    status: Optional[str] = Field(default="payment")
    description: Optional[str] = Field(default="bank payment")


class PaymentAllocationDB(PaymentAllocationBase, BaseMixin, table=True):
    __tablename__ = "payment_allocations_rls"

    # Correct foreign key definition
    payment_id: uuid.UUID = Field(        sa_column=Column(ForeignKey("payments_rls.id", ondelete="CASCADE"), nullable=False, index=True)    )
    invoice_id: uuid.UUID = Field(        sa_column=Column(ForeignKey("invoices_rls.id", ondelete="CASCADE"), nullable=False, index=True)    )
    invoice: "InvoiceDB" = Relationship(back_populates="payment_allocations")
    payment: Optional["PaymentDB"] = Relationship(back_populates="payment_allocations")

        

class PaymentAllocationCreate(PaymentAllocationBase):
    payment_id: uuid.UUID
    invoice_id: uuid.UUID


class PaymentAllocationRead(PaymentAllocationBase):
    id: uuid.UUID
    payment_id: uuid.UUID
    invoice_id: uuid.UUID
    is_deleted: bool = Field(default=False)  # soft delete flag


class PaymentAllocationUpdate(SQLModel):
    allocated_amount: float | None = None
    allocated_at: datetime | None = None
    version: int | None = None
    status: str | None = None
    description: str | None = None
    payment_id: uuid.UUID | None = None
    invoice_id: uuid.UUID | None = None
    is_deleted: bool | None = None
