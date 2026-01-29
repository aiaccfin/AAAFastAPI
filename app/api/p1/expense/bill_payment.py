from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, SQLModel
from typing import List, Optional, Dict, Any
from datetime import datetime
import uuid

from app.db.connection.conn_rls import tenant_session_dependency
from app.models.rls.m_bill_payment_rls import BillPaymentCreate, BillPaymentRead, BillPaymentVoid, BillPaymentWithAllocationsCreate
from app.services.service_bill_payment import bill_payment_service


router = APIRouter()
TENANT_ID = uuid.UUID("550e8400-e29b-41d4-a716-446655440000")

get_session = tenant_session_dependency(TENANT_ID)


@router.get("/", response_model=List[BillPaymentRead], description="Get all bill payments")
async def get_all_bill_payments(session: Session = Depends(get_session)):
    """Get all bill payments"""
    return bill_payment_service.list_payments(session)


@router.post("/", description="""This endpoint: </br>
    1. Creates the bill payment (if source_type="payment") </br>
    2. OR applies vendor credits (if source_type="credit") </br>
    3. Creates allocation rows for each bill </br>
    4. Updates bill amounts (amount_paid/amount_credited, balance_due, payment_status) </br>
    5. Updates vendor credit records when credits are applied""")
async def create_bill_payment(
    data: BillPaymentWithAllocationsCreate,
    session: Session = Depends(get_session)
):
    """
    Create a bill payment and allocate it to bills, OR apply credits to bills.
    
    If allocations have source_type="credit", applies credits instead of creating payment.
    Otherwise creates payment and allocations.
    
    This endpoint:
    1. Creates the bill payment (if source_type="payment")
    2. OR applies vendor credits (if source_type="credit")
    3. Creates allocation rows for each bill
    4. Updates bill amounts (amount_paid/amount_credited, balance_due, payment_status)
    5. Updates vendor credit records when credits are applied
    """
    try:
        # Check if any allocation is a credit application
        credit_allocations = [a for a in data.allocations if a.source_type == "credit"]
        payment_allocations = [a for a in data.allocations if a.source_type == "payment"]
        
        all_created_allocations = []
        new_payment = None
        
        # If there are credit allocations, apply credits (without committing)
        if credit_allocations:
            # Group by credit_id (source_id)
            from collections import defaultdict
            credits_by_id = defaultdict(list)
            for alloc in credit_allocations:
                credits_by_id[alloc.source_id].append(alloc)
            
            # Apply each credit (commit=False to keep in same transaction)
            for credit_id, allocations in credits_by_id.items():
                created = bill_payment_service.apply_credit_to_bills(
                    credit_id=credit_id,
                    allocations=allocations,
                    tenant_id=TENANT_ID,
                    session=session,
                    commit=False  # Don't commit yet, wait for single transaction
                )
                all_created_allocations.extend(created)
        
        # If there are payment allocations, create payment (without committing)
        if payment_allocations:
            # Extract journal_lines before creating payment
            journal_lines_data = getattr(data, 'journal_lines', None)
            
            payment_data = BillPaymentCreate(
                amount=data.amount,
                payment_date=data.payment_date or datetime.utcnow(),
                payee_id=data.payee_id,
                payee_snapshot=data.payee_snapshot,
                payment_method=data.payment_method,
                deposit_account_id=data.deposit_account_id,
                reference_no=data.reference_no,
                notes=data.notes or {},
                amount_paid=data.amount_paid,
                reference_id=data.reference_id,
                extras=data.extras or {}
            )
            new_payment = bill_payment_service.create_bill_payment_with_allocations(
                payment_data=payment_data,
                allocations=payment_allocations,
                tenant_id=TENANT_ID,
                session=session,
                commit=False,  # Don't commit yet, wait for single transaction
                journal_lines_data=journal_lines_data
            )
        
        # Commit everything in a single transaction
        try:
            session.commit()
            # Refresh objects after commit
            if new_payment:
                session.refresh(new_payment)
            for allocation in all_created_allocations:
                session.refresh(allocation)
        except Exception as e:
            session.rollback()
            raise
        
        # Return appropriate response
        if credit_allocations and payment_allocations:
            return {"message": "Credits and payment applied", "payment": new_payment, "credit_allocations": all_created_allocations}
        elif credit_allocations:
            return {"message": "Credits applied", "allocations": all_created_allocations}
        else:
            return new_payment
            
    except ValueError as e:
        session.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=500, detail=f"Error processing request: {str(e)}")


@router.patch("/{payment_id}/void", response_model=BillPaymentRead, description="Void a bill payment")
async def void_bill_payment(
    payment_id: uuid.UUID,
    data: BillPaymentVoid = BillPaymentVoid(),
    session: Session = Depends(get_session)
):
    """Void a bill payment by reversing the journal and optionally creating a new one"""
    try:
        journal_lines_data = getattr(data, 'journal_lines', None)
        voided_payment = bill_payment_service.void_bill_payment(
            payment_id, 
            session,
            journal_lines_data=journal_lines_data
        )
        # Convert amounts from cents to dollars
        payment_dict = voided_payment.dict()
        if 'amount' in payment_dict and payment_dict['amount'] is not None:
            payment_dict['amount'] = payment_dict['amount'] / 100.0
        if 'amount_paid' in payment_dict and payment_dict.get('amount_paid') is not None:
            payment_dict['amount_paid'] = payment_dict['amount_paid'] / 100.0
        return BillPaymentRead(**payment_dict)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error voiding payment: {str(e)}")


@router.patch("/{payment_id}/delete", response_model=BillPaymentRead, description="Soft delete a bill payment")
async def soft_delete_bill_payment(
    payment_id: uuid.UUID,
    session: Session = Depends(get_session)
):
    """Soft delete a bill payment by reversing all allocations and marking as deleted"""
    try:
        deleted_payment = bill_payment_service.soft_delete_bill_payment(payment_id, session)
        # Convert amounts from cents to dollars
        payment_dict = deleted_payment.dict()
        if 'amount' in payment_dict and payment_dict['amount'] is not None:
            payment_dict['amount'] = payment_dict['amount'] / 100.0
        if 'amount_paid' in payment_dict and payment_dict.get('amount_paid') is not None:
            payment_dict['amount_paid'] = payment_dict['amount_paid'] / 100.0
        return BillPaymentRead(**payment_dict)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting payment: {str(e)}")

