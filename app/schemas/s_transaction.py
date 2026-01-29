from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class Transaction(BaseModel):
    transaction_id: str = Field(..., description="Unique ID for the transaction")
    invoice_id: str = Field(..., description="Linked invoice ID")
    amount: float = Field(..., description="Payment amount")
    method: str = Field(..., description="Payment method (e.g., cash, card, bank)")
    type: str = Field("payment", description="Transaction type")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    class Config:
        extra = "allow"  # allow user to add new fields dynamically


