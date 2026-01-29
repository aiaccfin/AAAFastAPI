import uuid
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session, select
from app.db.connection.conn_rls import get_super_session_factory

from app.models.rls.m_payment_rls import PaymentCreate, PaymentRead, PaymentDB, PaymentUpdate, PmtAllocRead
from app.models.rls.m_payment_allocation_rls import PaymentAllocationCreate, PaymentAllocationRead
from app.models.rls.m_payment_workflow import PaymentWorkflow

from app.services.service_payment import payment_service
from app.services.service_inv import inv_service

from sqlalchemy.exc import SQLAlchemyError
from sqlmodel import Session
# from app.db.connection.conn_rls import engine_rls_create

router = APIRouter()
TENANT_ID = "550e8400-e29b-41d4-a716-446655440000"

fun_get_session = get_super_session_factory()

@router.get("/list_payments/", response_model=list[PaymentRead])
async def list_payments(
    session: Session = Depends(fun_get_session)
):
    return payment_service.list_payments(session)


@router.post("/generate_payment", response_model=PaymentRead)
async def create_payment(
        data: PaymentCreate,
        session: Session = Depends(fun_get_session)
):
    new_payment = payment_service.create_payment(data, TENANT_ID, session)
    return new_payment



@router.patch("/payment/{pmt_id}", response_model=PaymentRead, summary="Update an existing pmt")
async def update_payment(
    pmt_id: uuid.UUID,
    data: PaymentUpdate,
    session: Session = Depends(fun_get_session),
):
    """Update an existing invoice"""
    updated = payment_service.update_payment(pmt_id, data, session)

    if not updated:
        raise HTTPException(status_code=404, detail="Invoice not found")

    return updated


# @router.get("/list_allocation", response_model=list[PaymentAllocationRead])
# async def list_payment_allocations(session: Session = Depends(fun_get_session)):
#     return payment_service.list_payment_allocations(session)


# @router.post("/generate_allocation", response_model=PaymentAllocationRead)
# async def create_payment_allocation(data: PaymentAllocationCreate, session: Session = Depends(fun_get_session)):
#     new_payment_allocation = payment_service.create_payment_allocation(
#         data, TENANT_ID, session)
#     return new_payment_allocation


# @router.patch("/alloc/{alloc_id}", response_model=PaymentAllocationRead, summary="Update an existing allocation")
# async def patch_alloc(
#     alloc_id: uuid.UUID,
#     data: PaymentAllocationRead,
#     session: Session = Depends(fun_get_session),
# ):
#     """Update an existing invoice"""
#     updated = payment_service.update_allocation(alloc_id, data, session)

#     if not updated:
#         raise HTTPException(status_code=404, detail="allocation not found")

#     return updated


@router.get("/get/{pmt_id}", response_model=PmtAllocRead, summary="Get by ID")
async def get_payment(
        pmt_id: uuid.UUID,
        session: Session = Depends(fun_get_session)
):
    """Get a specific invoice by ID"""
    invoice = payment_service.get_payment_by_id(pmt_id=pmt_id, session=session)

    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")
    return invoice


# @router.post("/post_pmt_alloc_inv", summary="Create payment + allocations + invoices bundle")
# async def generate_bundle(
#     data: PaymentWorkflow,
# ):
#     with Session(engine_rls_create) as session:
#         try:
#             results = {}

#             # 1️⃣ Create payment
#             payment = payment_service.create_payment(
#                 data.payment, TENANT_ID, session)
#             results["payment"] = payment

#             payment_id = payment.id

#             # 2️⃣ Create invoices
#             invoices = []
#             for inv in data.invoices_update:
#                 invoices.append(
#                     inv_service.update_invoice(inv.id, inv, session))
#             results["invoices"] = invoices

#             # 3️⃣ Create allocations
#             allocations = []
#             for alloc in data.allocations:
#                 if alloc.version == 2:                    # Credit note allocation: keep original payment_id
#                     pass
#                 else:
#                     alloc.payment_id = payment_id      # 🔥 inject payment_id
#                 allocations.append(payment_service.create_payment_allocation(
#                     alloc, TENANT_ID, session))
#             results["allocations"] = allocations

#             # Final commit
#             session.commit()
#             return results

#         except Exception:
#             session.rollback()
#             raise



