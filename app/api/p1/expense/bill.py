import uuid
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session

from app.db.connection.conn_rls import tenant_session_dependency
from app.models.rls.m_bill_rls import BillRead, BillCreate, BillUpdate, BillDelete
from app.services.service_bill import bill_service
from app.models.rls.m_pagination import PaginatedResponse


router = APIRouter()
TENANT_ID = uuid.UUID("550e8400-e29b-41d4-a716-446655440000")

get_session = tenant_session_dependency(TENANT_ID)


@router.get("/all", response_model=list[BillRead], description="Get all bill records")
async def get_all_bills(session: Session = Depends(get_session)):
    return bill_service.get_all_bills(session)


@router.get("/", response_model=PaginatedResponse, description="List all bills")
async def list_bills(
    session: Session = Depends(tenant_session_dependency(TENANT_ID)),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    status: str | None = None,
    payment_status: str | None = None,
    issue_date_start: datetime | None = None,
    issue_date_end: datetime | None = None,
):
    return bill_service.list_bills(
        session=session,
        page=page,
        page_size=page_size,
        status=status,
        payment_status=payment_status,
        issue_date_start=issue_date_start,
        issue_date_end=issue_date_end,
    )


@router.post("/", response_model=BillRead, description="Create a new bill")
async def create_bill(
    data: BillCreate,
    session: Session = Depends(tenant_session_dependency(TENANT_ID))
):
    new_bill = bill_service.create_bill(
        data=data,
        tenant_id=TENANT_ID,
        session=session
    )
    return new_bill


# @router.post("/credit-card-credit", response_model=BillRead, description="Create a new credit card credit")
# async def create_credit_card_credit(
#     data: BillCreate,
#     session: Session = Depends(tenant_session_dependency(TENANT_ID))
# ):
#     new_credit = bill_service.create_credit_card_credit(
#         data=data,
#         tenant_id=TENANT_ID,
#         session=session
#     )
#     return new_credit


@router.get("/{bill_id}", response_model=BillRead, description="Get a specific bill by ID")
async def get_bill(
    bill_id: uuid.UUID,
    session: Session = Depends(get_session)
):
    """Get a specific bill by ID"""
    bill = bill_service.get_bill_by_id(bill_id, session)

    if not bill:
        raise HTTPException(status_code=404, detail="Bill not found")
    return bill


@router.patch("/{bill_id}", response_model=BillRead, description="Update an existing bill")
async def update_bill(
    bill_id: uuid.UUID,
    data: BillUpdate,
    session: Session = Depends(get_session),
):
    updated_bill = bill_service.update_bill(bill_id=bill_id, data=data, session=session)
    if not updated_bill:
        raise HTTPException(status_code=404, detail="Bill not found")
    return updated_bill


@router.patch("/{bill_id}/delete", response_model=BillRead, description="Soft delete a bill")
async def soft_delete_bill(
    bill_id: uuid.UUID,
    data: BillDelete,
    session: Session = Depends(get_session),
):
    deleted_bill = bill_service.soft_delete_bill(bill_id=bill_id, data=data, session=session)
    if not deleted_bill:
        raise HTTPException(status_code=404, detail="Bill not found")
    return deleted_bill
