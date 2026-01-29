import uuid
from datetime import datetime
from typing import List, Literal
from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlmodel import Session, select

from app.db.connection.conn_rls import get_tenant_session, tenant_session_dependency, tenant_session_dependency
from app.models.rls.m_invoice_rls import InvoiceRead, InvoiceDB, InvoiceCreate, InvoiceUpdate, InvoiceReadList, InvoiceDelete
from app.services.service_inv import inv_service
from app.models.rls.m_pagination import PaginatedResponse


router = APIRouter()
TENANT_ID = "550e8400-e29b-41d4-a716-446655440000"

get_session = tenant_session_dependency(TENANT_ID)

DOC_TYPE_MAP = {
    "/invoice": "invoice",
    "/receipt": "receipt",
    "/credits": "credits",
    "/all": None,
}


@router.get("/invoice", summary="Invoice List")
@router.get("/receipt", summary="Receipt List")
@router.get("/credits", summary="credits List")
@router.get("/all", summary="All Documents")
async def list_invoices_and_receipts(
    request: Request,
    session: Session = Depends(tenant_session_dependency(TENANT_ID)),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    status: str | None = None,
    payment_status: str | None = None,
    issue_date_start: datetime | None = None,
    issue_date_end: datetime | None = None,
):
    # Pass path directly
    doc_type = DOC_TYPE_MAP.get(request.url.path)
    return inv_service.list_inv_rec(
        session=session,
        page=page,
        page_size=page_size,
        status=status,
        payment_status=payment_status,
        issue_date_start=issue_date_start,
        issue_date_end=issue_date_end,
        doc_type=doc_type,
    )


@router.post("/invoice", response_model=InvoiceRead, summary="Create a new invoice")
@router.post("/receipt", response_model=InvoiceRead, summary="Create a new receipt")
@router.post("/credits", response_model=InvoiceRead, summary="Create a new credit")
async def create_invoice(
        request: Request,
        data: InvoiceCreate,
        session: Session = Depends(tenant_session_dependency(TENANT_ID))):

    doc_type = DOC_TYPE_MAP.get(request.url.path)
    new_invoice = inv_service.create_inv_rec(
        data=data,
        tenant_id=TENANT_ID,
        doc_type=doc_type,
        session=session,)
    
    return new_invoice


@router.get("/invoice/next-invoice-number", summary="Get next invoice number")
@router.get("/receipt/next-receipt-number", summary="Get next receipt number")
@router.get("/credits/next-credit-number", summary="Get next credit number")
async def get_next_number_endpoint(
    request: Request,
    session: Session = Depends(tenant_session_dependency(TENANT_ID)),
):
    doc_type = DOC_TYPE_MAP.get(request.url.path[0:8])
    print("PATH:", request.url.path)
    print("SLICE:", request.url.path[0:8])

    try:
        if doc_type == "invoice":
            next_number = inv_service.get_next_invoice_number_for_me(
                session, TENANT_ID
            )
            return {"next_invoice_number": next_number}

        elif doc_type == "receipt":
            next_number = inv_service.get_next_receipt_number_for_me(
                session, TENANT_ID
            )
            return {"next_receipt_number": next_number}

        elif doc_type == "credits":
            next_number = inv_service.get_next_credits_number_for_me(
                session, TENANT_ID
            )
            return {"next_credit_number": next_number}

        else:
            raise HTTPException(status_code=400, detail="Invalid doc_type")

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/byid/{_id}", response_model=InvoiceRead, summary="Get a specific invoice/receipt by ID")
async def get_invoice(invoice_id: uuid.UUID,    session: Session = Depends(get_session)):
    """Get a specific invoice by ID"""
    invoice = inv_service.get_invoice_by_id(invoice_id, session)

    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")
    return invoice


@router.patch("/{invoice_id}", response_model=InvoiceRead, summary="Update an existing invoice")
async def update_invoice(
    invoice_id: uuid.UUID,
    data: InvoiceUpdate,
    session: Session = Depends(get_session),
):
    """Update an existing invoice"""
    updated = inv_service.update_invoice(invoice_id, data, session)

    if not updated:
        raise HTTPException(status_code=404, detail="Invoice not found")

    return updated


@router.patch("/delete/{invoice_id}", response_model=InvoiceRead, summary="Soft delete an existing invoice/receipt")
async def soft_delete_invoice(
    invoice_id: uuid.UUID,
    data: InvoiceDelete,
    session: Session = Depends(get_session),
):
    """Update an existing invoice"""
    updated = inv_service.update_invoice(invoice_id, data, session)

    if not updated:
        raise HTTPException(status_code=404, detail="Invoice not found")

    return updated


@router.get("/customer/{customer_id}", response_model=List[InvoiceReadList], summary="Get all invoices/receipts for a specific customer")
async def get_invoices_by_customer(
    customer_id: str,    session: Session = Depends(get_session)
):
    return inv_service.get_invoices_by_customer(session, customer_id)


# @router.get("/receipt/{receipt_number}", response_model=InvoiceRead, summary="Get by number")
@router.get("/number/{number}", response_model=InvoiceRead,  summary="Get by number")
async def get_invoice_by_number(
    number: str,
    session: Session = Depends(get_session)
):
    """Get a specific invoice by ID"""
    invoice = inv_service.get_invoice_by_number(number, session)

    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice/receipt not found")

    return invoice


