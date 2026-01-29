from pydantic import BaseModel
from datetime import date
from typing import Optional, List

class TransactionAI(BaseModel):
    date: date
    description: str
    amount: float
    transaction_type: str
    reference: Optional[str] = None
    balance_after: Optional[float] = None

class SummaryAI(BaseModel):
    account_number: str
    account_name: str
    bank_name: str
    statement_period_start: date
    statement_period_end: date
    opening_balance: float
    closing_balance: float
    currency: str = "USD"

class BankStatementAI(BaseModel):
    summary: SummaryAI
    transactions: List[TransactionAI]