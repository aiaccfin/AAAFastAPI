import uuid
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session, select
from app.db.connection.conn_rls import get_tenant_session, tenant_session_dependency, tenant_session_dependency
from app.models.rls.m_payment_rls  import PaymentCreate, PaymentRead, PaymentDB, PaymentUpdate
from app.models.rls.m_payment_allocation_rls  import PaymentAllocationCreate, PaymentAllocationRead
from app.services.service_payment import payment_service
from app.models.rls.m_payment_workflow import PaymentWorkflow
from sqlalchemy.exc import SQLAlchemyError

router = APIRouter()
TENANT_ID = "550e8400-e29b-41d4-a716-446655440000"

get_session = tenant_session_dependency(TENANT_ID)


@router.get("/", response_model=list[PaymentRead])
async def list_payments(session: Session = Depends(tenant_session_dependency(TENANT_ID))):
    return payment_service.list_payments(session)


@router.post("/", response_model=PaymentRead)
async def create_payment(data: PaymentCreate, session: Session = Depends(tenant_session_dependency(TENANT_ID))):
    new_payment = payment_service.create_payment(data, TENANT_ID, session)
    return new_payment


@router.get("/payment_allocation", response_model=list[PaymentAllocationRead])
async def list_payment_allocations(session: Session = Depends(tenant_session_dependency(TENANT_ID))):
    return payment_service.list_payment_allocations(session)


@router.post("/payment_allocation", response_model=PaymentAllocationRead)
async def create_payment_allocation(data: PaymentAllocationCreate, session: Session = Depends(tenant_session_dependency(TENANT_ID))):
    # Use the service to create the payment allocation
    new_payment_allocation = payment_service.create_payment_allocation(data, TENANT_ID, session)
    return new_payment_allocation



@router.get("/{_id}", response_model=PaymentRead, summary="Get by ID")
async def get_payment(pmt_id: uuid.UUID,    session: Session = Depends(get_session)):
    """Get a specific invoice by ID"""
    invoice = payment_service.get_payment_by_id(pmt_id=pmt_id, session=session)

    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")
    return invoice


@router.patch("/{pmt_id}", response_model=PaymentRead, summary="Update an existing pmt")
async def update_payment(
    pmt_id: uuid.UUID,
    data: PaymentUpdate,
    session: Session = Depends(get_session),
):
    """Update an existing invoice"""
    updated = payment_service.update_payment(pmt_id, data, session)

    if not updated:
        raise HTTPException(status_code=404, detail="Invoice not found")

    return updated



@router.post("/dispatch", summary="General payment + allocation workflow")
async def payment_dispatch(
    data: PaymentWorkflow,
    session: Session = Depends(tenant_session_dependency(TENANT_ID))
):
    """
    Flexible workflow endpoint for creating:
    - payment
    - allocations
    - invoice updates
    all inside a single transaction.
    """

    try:
        with session.begin():  # ensures atomicity

            result = {
                "payment": None,
                "allocations": [],
                "invoice_updates": []
            }

            # 1️⃣ Handle Payment first
            if data.payment:
                result["payment"] = payment_service.create_payment(
                    data.payment, TENANT_ID, session
                )

            # 2️⃣ Handle Payment Allocations (depends on payment existing)
            if data.allocations:
                for alloc in data.allocations:
                    new_alloc = payment_service.create_payment_allocation(
                        alloc, TENANT_ID, session
                    )
                    result["allocations"].append(new_alloc)

            # 3️⃣ Handle Invoice Updates (optional)
            # NOTE: this is flexible until you finalize the design
            if data.invoice_updates:
                for inv in data.invoice_updates:
                    invoice_id = inv.get("invoice_id")
                    payload = inv.get("data", {})
                    updated = payment_service.update_invoice(invoice_id, payload, session)
                    result["invoice_updates"].append(updated)

        return result

    except SQLAlchemyError as e:
        session.rollback()
        raise HTTPException(
            status_code=400,
            detail=f"Transaction failed: {str(e)}"
        )


@router.patch("/dispatch", summary="General update workflow for payment + allocation + invoice")
async def payment_dispatch_patch(
    data: PaymentWorkflow,
    session: Session = Depends(tenant_session_dependency(TENANT_ID))
):
    """
    Flexible workflow endpoint for updating:
    - payment
    - allocations
    - invoices
    all inside a single atomic transaction.
    """

    try:
        with session.begin():

            result = {
                "payment": None,
                "allocations": [],
                "invoice_updates": []
            }

            # 1️⃣ Update Payment (same pattern as update_payment endpoint)
            if data.payment:
                if not data.payment.id:
                    raise HTTPException(
                        status_code=400,
                        detail="Payment update requires an 'id'"
                    )

                result["payment"] = payment_service.update_payment(
                    pmt_id=data.payment.id,
                    data=data.payment,
                    session=session
                )

            # 2️⃣ Update Allocations
            if data.allocations:
                for alloc in data.allocations:
                    if not alloc.id:
                        raise HTTPException(
                            status_code=400,
                            detail="Allocation update requires an 'id'"
                        )

                    updated_alloc = payment_service.update_payment_allocation(
                        alloc_id=alloc.id,
                        data=alloc,
                        session=session
                    )
                    result["allocations"].append(updated_alloc)

            # 3️⃣ Update Invoices (same pattern as invoice patch endpoint)
            if data.invoice_updates:
                for inv in data.invoice_updates:
                    invoice_id = inv.get("invoice_id")
                    payload = inv.get("data", {})

                    updated = payment_service.update_invoice(
                        invoice_id,
                        payload,
                        session
                    )
                    result["invoice_updates"].append(updated)

        return result

    except SQLAlchemyError as e:
        session.rollback()
        raise HTTPException(
            status_code=400,
            detail=f"Transaction failed: {str(e)}"
        )
