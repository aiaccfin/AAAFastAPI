import uuid
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session

from app.db.connection.conn_rls import tenant_session_dependency
from app.models.rls.m_bill_rls import BillRead, BillCreate
from app.services.service_credit_card_credit import credit_card_credit_service
from app.models.rls.m_pagination import PaginatedResponse


router = APIRouter()
TENANT_ID = uuid.UUID("550e8400-e29b-41d4-a716-446655440000")

get_session = tenant_session_dependency(TENANT_ID)


@router.get("/", response_model=PaginatedResponse, description="List all credit card credits")
async def list_credit_card_credits(
    session: Session = Depends(tenant_session_dependency(TENANT_ID)),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    status: str | None = None,
    payment_status: str | None = None,
    issue_date_start: datetime | None = None,
    issue_date_end: datetime | None = None,
):
    return credit_card_credit_service.list_credits(
        session=session,
        page=page,
        page_size=page_size,
        status=status,
        payment_status=payment_status,
        issue_date_start=issue_date_start,
        issue_date_end=issue_date_end,
    )


@router.post("/", response_model=BillRead, description="Create a new credit card credit")
async def create_credit_card_credit(
    data: BillCreate,
    session: Session = Depends(tenant_session_dependency(TENANT_ID))
):
    new_credit = credit_card_credit_service.create_credit(
        data=data,
        tenant_id=TENANT_ID,
        session=session
    )
    return new_credit


@router.get("/{credit_id}", response_model=BillRead, description="Get a specific credit card credit by ID")
async def get_credit_card_credit(
    credit_id: uuid.UUID,
    session: Session = Depends(get_session)
):
    credit = credit_card_credit_service.get_credit_by_id(credit_id, session)

    if not credit:
        raise HTTPException(status_code=404, detail="Credit card credit not found")
    return credit

