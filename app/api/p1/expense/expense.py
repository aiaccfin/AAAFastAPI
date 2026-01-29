import uuid
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session

from app.db.connection.conn_rls import tenant_session_dependency
from app.models.rls.m_bill_rls import BillRead, BillCreate
from app.services.service_expense import expense_service
from app.models.rls.m_pagination import PaginatedResponse


router = APIRouter()
TENANT_ID = uuid.UUID("550e8400-e29b-41d4-a716-446655440000")

get_session = tenant_session_dependency(TENANT_ID)


@router.get("/", response_model=PaginatedResponse, description="List all expenses")
async def list_expenses(
    session: Session = Depends(tenant_session_dependency(TENANT_ID)),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    status: str | None = None,
    payment_status: str | None = None,
    issue_date_start: datetime | None = None,
    issue_date_end: datetime | None = None,
):
    return expense_service.list_expenses(
        session=session,
        page=page,
        page_size=page_size,
        status=status,
        payment_status=payment_status,
        issue_date_start=issue_date_start,
        issue_date_end=issue_date_end,
    )


@router.post("/", response_model=BillRead, description="Create a new expense")
async def create_expense(
    data: BillCreate,
    session: Session = Depends(tenant_session_dependency(TENANT_ID))
):
    new_expense = expense_service.create_expense(
        data=data,
        tenant_id=TENANT_ID,
        session=session
    )
    return new_expense


@router.get("/{expense_id}", response_model=BillRead, description="Get a specific expense by ID")
async def get_expense(
    expense_id: uuid.UUID,
    session: Session = Depends(get_session)
):
    expense = expense_service.get_expense_by_id(expense_id, session)

    if not expense:
        raise HTTPException(status_code=404, detail="Expense not found")
    return expense

