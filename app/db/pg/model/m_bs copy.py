from __future__ import annotations
from typing import Optional, List
from datetime import date, datetime
from sqlmodel import SQLModel, Field, Relationship


class BSSummary(SQLModel, table=True):
    __tablename__ = "bs_summary"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: Optional[int] = Field(default=None)
    bank_name: Optional[str] = None
    account_number: Optional[str] = Field(default=None)

    statement_period_start: Optional[date] = None
    statement_period_end: Optional[date] = None

    opening_balance: Optional[float] = None
    closing_balance: Optional[float] = None
    currency: Optional[str] = Field(default="USD")

    source_file: Optional[str] = None
    created_at: Optional[datetime] = Field(default_factory=datetime.utcnow)

    transactions: List["BSDetail"] = Relationship(back_populates="statement")


class BSDetail(SQLModel, table=True):
    __tablename__ = "bs_detail"

    id: Optional[int] = Field(default=None, primary_key=True)

    transaction_date: Optional[date] = None
    description: Optional[str] = None
    amount: Optional[float] = None
    type: Optional[str] = Field(default=None)
    balance: Optional[float] = None
    category: Optional[str] = None
    note: Optional[str] = None

    statement_id: Optional[int] = Field(default=None, foreign_key="bs_summary.id")
    statement: Optional[BSSummary] = Relationship(back_populates="transactions")
