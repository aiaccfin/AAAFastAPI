from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

class BankStatement(BaseModel):
    uuid: str = Field(..., description="Unique UUID for the bank statement")
    account_id: str = Field(..., description="Account ID associated with the bank statement")
    account_name: str = Field(..., description="Account holder's name")
    bank_name: str = Field(..., description="Name of the bank")
    period_start: datetime = Field(..., description="Start date of the statement period")
    period_end: datetime = Field(..., description="End date of the statement period")
    opening_balance: float = Field(..., description="Opening balance of the account")
    closing_balance: float = Field(..., description="Closing balance of the account")
    currency: str = Field(default="USD", description="Currency used for the statement")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Date and time when the statement was created")
    updated_at: datetime = Field(default_factory=datetime.utcnow, description="Date and time when the statement was last updated")
    
    transactions: List['Transaction'] = Field(default=[], description="List of transactions in the bank statement")

    class Config:
        extra = "allow"  # Allow additional fields

class Transaction(BaseModel):
    transaction_id: str = Field(..., description="Unique ID for the transaction")
    description: str = Field(..., description="Transaction description")
    amount: float = Field(..., description="Amount of the transaction")
    transaction_type: str = Field(..., description="Type of the transaction (e.g., debit, credit)")
    reference: Optional[str] = Field(None, description="Reference for the transaction, if available")
    balance_after: float = Field(..., description="Balance after the transaction")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Date and time when the transaction was created")
    updated_at: datetime = Field(default_factory=datetime.utcnow, description="Date and time when the transaction was last updated")

    class Config:
        extra = "allow"  # Allow additional fields
