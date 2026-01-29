from typing import Optional, List, Dict, Any
from pydantic import BaseModel
from app.models.rls.m_payment_rls import PaymentCreate, PaymentUpdate
from app.models.rls.m_payment_allocation_rls import PaymentAllocationCreate, PaymentAllocationRead
from app.models.rls.m_invoice_rls import InvoiceUpdate

class PaymentWorkflow(BaseModel):
    payment: Optional[PaymentCreate] = None
    allocations: Optional[List[PaymentAllocationCreate]] = None
    invoices_update: Optional[List[InvoiceUpdate]] = None


class UpdatePaymentWorkflow(BaseModel):
    payment: Optional[PaymentUpdate] = None
    allocations: Optional[List[PaymentAllocationRead]] = None
    invoices_update: Optional[List[InvoiceUpdate]] = None
