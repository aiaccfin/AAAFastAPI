import uuid
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session

from app.db.connection.conn_rls import tenant_session_dependency
from app.models.rls.m_bill_rls import BillRead, BillCreate
from app.services.service_vendor_credit import vendor_credit_service
from app.models.rls.m_pagination import PaginatedResponse


router = APIRouter()
TENANT_ID = uuid.UUID("550e8400-e29b-41d4-a716-446655440000")

get_session = tenant_session_dependency(TENANT_ID)


@router.get("/", response_model=PaginatedResponse, description="List all vendor credits")
async def list_vendor_credits(
    session: Session = Depends(tenant_session_dependency(TENANT_ID)),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    status: str | None = None,
    payment_status: str | None = None,
    issue_date_start: datetime | None = None,
    issue_date_end: datetime | None = None,
):
    return vendor_credit_service.list_vendor_credits(
        session=session,
        page=page,
        page_size=page_size,
        status=status,
        payment_status=payment_status,
        issue_date_start=issue_date_start,
        issue_date_end=issue_date_end,
    )


@router.post("/", response_model=BillRead, description="Create a new vendor credit")
async def create_vendor_credit(
    data: BillCreate,
    session: Session = Depends(tenant_session_dependency(TENANT_ID))
):
    new_vendor_credit = vendor_credit_service.create_vendor_credit(
        data=data,
        tenant_id=TENANT_ID,
        session=session
    )
    return new_vendor_credit


@router.get("/{vendor_credit_id}", response_model=BillRead, description="Get a specific vendor credit by ID")
async def get_vendor_credit(
    vendor_credit_id: uuid.UUID,
    session: Session = Depends(get_session)
):
    """Get a specific vendor credit by ID"""
    vendor_credit = vendor_credit_service.get_vendor_credit_by_id(vendor_credit_id, session)

    if not vendor_credit:
        raise HTTPException(status_code=404, detail="Vendor credit not found")
    return vendor_credit

