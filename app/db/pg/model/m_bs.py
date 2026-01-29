from typing import Optional, List
from datetime import datetime, date
from sqlmodel import SQLModel, Field, Relationship
from uuid import UUID, uuid4

# Bank Statement Summary Models
class BSSummaryBase(SQLModel):
    user_id: Optional[int] = Field(default=1, description="The owner/user ID")
    account_id: Optional[str] = Field(default="ACC123", description="Bank account identifier")
    
    account_number: Optional[str] = Field(default="123456789", description="Full account number")
    account_name: Optional[str] = Field(default="My Business Account", description="Account holder name")
    bank_name: Optional[str] = Field(default="Bank of Example", description="Bank institution name")
    
    period_start: Optional[date] = Field(default=date.today(), description="Start date of statement period")
    period_end: Optional[date] = Field(default=date.today(), description="End date of statement period")
    
    opening_balance: Optional[float] = Field(default=0.0, description="Opening balance")
    closing_balance: Optional[float] = Field(default=0.0, description="Closing balance")
    currency: Optional[str] = Field(default="CAD", description="Currency code")
    currency2: Optional[str] = Field(default="Statement Type not found", description="Statement type")
    uuid_string: Optional[str] = Field(default="CAD", description="Currency code")
    uuid: Optional[UUID] = Field(default=uuid4(), description="Currency code")

    is_locked: Optional[int] = Field(default=0)
    is_deleted: Optional[int] = Field(default=0)
    status: Optional[str] = Field(default="NEW", description="Status New?")
    
    created_at: Optional[str] = Field(default_factory=lambda: datetime.utcnow().isoformat())
    updated_at: Optional[str] = Field(default_factory=lambda: datetime.utcnow().isoformat())


class BSSummary(BSSummaryBase, table=True):
    __tablename__ = "bs_summary"
    id: Optional[int] = Field(default=None, primary_key=True)
    details: List["BSDetail"] = Relationship(back_populates="summary")


class BSSummaryCreate(BSSummaryBase):
    pass


class BSSummaryUpdate(BSSummaryBase):
    pass


class BSSummaryRead(BSSummaryBase):
    id: int
    details: List["BSDetailRead"] = []


# Bank Statement Detail Models
class BSDetailBase(SQLModel):
    summary_id: Optional[int] = Field(default=None, description="Related summary ID")
    biz_id: Optional[int] = Field(default=666, description="Related summary ID")
    user_id: Optional[int] = Field(default=888, description="Related summary ID")
    
    transaction_date: Optional[date] = Field(default=date.today(), description="Transaction date")
    description: Optional[str] = Field(default="Payment", description="Transaction description")
    amount: Optional[float] = Field(default=0.0, description="Transaction amount")
    
    transaction_type: Optional[str] = Field(default="debit", description="debit/credit")
    reference: Optional[str] = Field(default="REF123", description="Transaction reference")
    balance_after: Optional[float] = Field(default=0.0, description="Balance after transaction")
    
    category: Optional[str] = Field(default="uncategorized", description="Transaction category")
    notes: Optional[str] = Field(default="", description="Additional notes")

    uuid_string: Optional[str] = Field(default="uuidhere", description="Currency code")
    uuid: Optional[UUID] = Field(default=uuid4(), description="Currency code")
    
    is_reconciled: Optional[int] = Field(default=0)
    is_deleted: Optional[int] = Field(default=0)
    status: Optional[str] = Field(default="NEW", description="new?")
    
    created_at: Optional[str] = Field(default_factory=lambda: datetime.utcnow().isoformat())
    updated_at: Optional[str] = Field(default_factory=lambda: datetime.utcnow().isoformat())


class BSDetail(BSDetailBase, table=True):
    __tablename__ = "bs_detail"
    id: Optional[int] = Field(default=None, primary_key=True)
    summary_id: Optional[int] = Field(default=None, foreign_key="bs_summary.id")
    summary: Optional[BSSummary] = Relationship(back_populates="details")


class BSDetailCreate(BSDetailBase):
    pass


class BSDetailUpdate(BSDetailBase):
    pass


class BSDetailRead(BSDetailBase):
    id: int


# Include details in the summary read model after BSDetailRead is defined
BSSummaryRead.update_forward_refs()


class BSAllSummary(BSSummaryBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)