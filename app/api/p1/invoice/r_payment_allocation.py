import uuid
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session, select
from app.db.connection.conn_rls import get_super_session_factory

from app.models.rls.m_payment_allocation_rls import PaymentAllocationCreate, PaymentAllocationRead, PaymentAllocationUpdate
from app.models.rls.m_payment_workflow import PaymentWorkflow

from app.services.service_payment_allocation import payment_allocation_service 

from sqlmodel import Session
# from app.db.connection.conn_rls import engine_rls_create

router = APIRouter()
TENANT_ID = "550e8400-e29b-41d4-a716-446655440000"

fun_get_session = get_super_session_factory()


@router.get("/list_allocation", response_model=list[PaymentAllocationRead])
async def list_payment_allocations(session: Session = Depends(fun_get_session)):
    return payment_allocation_service.list_payment_allocations(session)


@router.post("/generate_allocation", response_model=PaymentAllocationRead)
async def create_payment_allocation(data: PaymentAllocationCreate, session: Session = Depends(fun_get_session)):
    new_payment_allocation = payment_allocation_service.create_payment_allocation(
        data, TENANT_ID, session)
    return new_payment_allocation


@router.patch("/alloc/{alloc_id}", response_model=PaymentAllocationRead, summary="Update an existing allocation")
async def patch_alloc(
    alloc_id: uuid.UUID,
    data: PaymentAllocationUpdate,
    session: Session = Depends(fun_get_session),
):
    """Update an existing invoice"""
    updated = payment_allocation_service.update_allocation(alloc_id, data, session)

    if not updated:
        raise HTTPException(status_code=404, detail="allocation not found")

    return updated


@router.get("/get/{alloc_id}", response_model=PaymentAllocationRead, summary="Get by ID")
async def get_alloc(
        alloc_id: uuid.UUID,
        session: Session = Depends(fun_get_session)
):
    """Get a specific invoice by ID"""
    invoice = payment_allocation_service.get_allocation_by_id(alloc_id=alloc_id, session=session)

    if not invoice:
        raise HTTPException(status_code=404, detail="alloc not found")
    return invoice