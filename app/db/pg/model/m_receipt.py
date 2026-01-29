from typing import Optional
from datetime import date
from sqlmodel import SQLModel, Field


class ReceiptBase(SQLModel):
    receipt_date: Optional[date] = None

    payer_name: Optional[str] = None
    payee_name: Optional[str] = None
    vendor_name: Optional[str] = None
    coa: Optional[str] = None

    subtotal: Optional[float] = None
    tax: Optional[float] = None
    total: Optional[float] = None

    currency: Optional[str] = "USD"
    payment_method: Optional[str] = None
    reference: Optional[str] = None
    description: Optional[str] = None



class Receipt(ReceiptBase, table=True):
    __tablename__ = "receipts" 
    id: Optional[int] = Field(default=None, primary_key=True)


class ReceiptCreate(ReceiptBase):
    pass

class ReceiptUpdate(ReceiptBase):
    pass

class ReceiptRead(ReceiptBase):
    id: int
