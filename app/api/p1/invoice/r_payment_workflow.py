import uuid
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session, select
from app.db.connection.conn_rls import get_super_session_factory

from app.models.rls.m_payment_rls import PaymentCreate, PaymentRead, PaymentDB, PaymentUpdate, PmtAllocRead
from app.models.rls.m_payment_allocation_rls import PaymentAllocationCreate, PaymentAllocationRead
from app.models.rls.m_payment_workflow import PaymentWorkflow, UpdatePaymentWorkflow

from app.services.service_payment import payment_service
from app.services.service_payment_allocation import payment_allocation_service
from app.services.service_inv import inv_service

from sqlmodel import Session
# from app.db.connection.conn_rls import engine_rls_create

router = APIRouter()
TENANT_ID = "550e8400-e29b-41d4-a716-446655440000"

fun_get_session = get_super_session_factory()


@router.post("/post_pmt_alloc_inv", summary="Create payment + allocations + invoices bundle")
async def generate_bundle(
    data: PaymentWorkflow,
):
    with Session(engine_rls_create) as session:
        try:
            results = {}

            # 1️⃣ Create payment
            payment = payment_service.create_payment(data.payment, TENANT_ID, session)
            results["payment"] = payment
            
            payment_id = payment.id

            # 2️⃣ Create invoices
            invoices = []
            for inv in data.invoices_update:
                invoices.append(inv_service.update_invoice(inv.id, inv, session))
            results["invoices"] = invoices

            # 3️⃣ Create allocations
            allocations = []
            for alloc in data.allocations:
                if alloc.version == 2:                    # Credit note allocation: keep original payment_id
                    pass
                else:
                    alloc.payment_id = payment_id      # 🔥 inject payment_id
                allocations.append(payment_service.create_payment_allocation(alloc, TENANT_ID, session))
            results["allocations"] = allocations

            # Final commit
            session.commit()
            return results

        except Exception:
            session.rollback()
            raise






@router.patch("/patch_pmt_alloc_inv", summary="Patch payment + allocations + invoices bundle")
async def patch_bundle(
    data: UpdatePaymentWorkflow,
):
    with Session(engine_rls_create) as session:
        try:
            results = {}

            # 1️⃣ Create payment
            updated = payment_service.update_payment(data.payment.id, data.payment, session)
            results["payment"] = updated
            

            # 2️⃣ Create invoices
            invoices = []
            for inv in data.invoices_update:
                invoices.append(inv_service.update_invoice(inv.id, inv, session))
            results["invoices"] = invoices


            # 3️⃣ Create allocations
            allocations = []
            for alloc in data.allocations:
                allocations.append(payment_allocation_service.update_allocation(alloc.id, alloc, session))

            results["allocations"] = allocations

            # Final commit
            session.commit()
            return results

        except Exception:
            session.rollback()
            raise



