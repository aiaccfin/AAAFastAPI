from typing import Optional
from datetime import date
from sqlmodel import SQLModel, Field


class InvoiceBase(SQLModel):
    invoice_number: Optional[str] = None
    biz_id: Optional[int] = None
    biz_name: Optional[str] = None
    customer_id: Optional[int] = None
    customer_name: Optional[str] = None
    client_id: Optional[int] = None
    client_name: Optional[str] = None
    client_address: Optional[str] = None
    client_payment_method: Optional[str] = None
    issue_date: Optional[date] = None
    due_date: Optional[date] = None
    payment_status: Optional[str] = None
    item_description: Optional[str] = None
    item_quantity: Optional[float] = None
    item_unit_price: Optional[float] = None
    item_tax_rate: Optional[float] = None
    item_tax: Optional[float] = None
    item_amount: Optional[float] = None
    invoice_total_amount: Optional[float] = None
    invoice_recurring: Optional[bool] = None
    invoice_note: Optional[str] = None

class Invoice(InvoiceBase, table=True):
    __tablename__ = "invoices" 
    id: Optional[int] = Field(default=None, primary_key=True)


class InvoiceCreate(InvoiceBase):
    pass


class InvoiceRead(InvoiceBase):
    id: int

class InvoiceUpdate(SQLModel):
    pass