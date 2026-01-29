# app/services/service_bill_payment.py
from typing import Optional, List
import uuid
from datetime import datetime
from sqlmodel import Session, select
from app.repositories.repository_bill_payment import bill_payment_repository
from app.repositories.repository_bill import bill_repository
from app.models.rls.m_bill_payment_rls import BillPaymentDB, BillPaymentCreate, BillPaymentRead
from app.models.rls.m_bill_payment_allocation_rls import BillPaymentAllocationDB, BillPaymentAllocationCreate
from app.models.rls.m_bill_rls import BillDB
from app.models.rls.m_journal_line_rls import JournalLineCreate
from app.services.service_journal import journal_service

class BillPaymentService:
    
    def list_payments(self, session: Session) -> List[BillPaymentRead]:
        """
        Get all bill payments.
        
        Args:
            session: Database session
            
        Returns:
            List of BillPaymentRead instances with amounts converted from cents to dollars
        """
        payments = bill_payment_repository.get_all_payments(session)
        result = []
        for payment in payments:
            # Convert amounts from cents to dollars
            payment_dict = payment.dict()
            if 'amount' in payment_dict and payment_dict['amount'] is not None:
                payment_dict['amount'] = payment_dict['amount'] / 100.0
            if 'amount_paid' in payment_dict and payment_dict.get('amount_paid') is not None:
                payment_dict['amount_paid'] = payment_dict['amount_paid'] / 100.0
            result.append(BillPaymentRead(**payment_dict))
        return result
    
    def create_bill_payment_with_allocations(
        self,
        payment_data: BillPaymentCreate,
        allocations: List[BillPaymentAllocationCreate],
        tenant_id: uuid.UUID,
        session: Session,
        commit: bool = True,
        journal_lines_data: Optional[List[JournalLineCreate]] = None
    ) -> BillPaymentDB:
        """
        Create a bill payment and its allocations, updating bill and credit amounts.
        
        Args:
            payment_data: The bill payment data
            allocations: List of allocations (can be bills or credits)
            tenant_id: Tenant ID
            session: Database session
            
        Returns:
            Created BillPaymentDB instance
        """
        # 1. Create the bill payment (convert amount to cents)
        payment_dict = payment_data.dict()
        # Convert amount from dollars to cents (multiply by 100)
        if 'amount' in payment_dict:
            payment_dict['amount'] = int(payment_dict['amount'] * 100)
        if 'amount_paid' in payment_dict and payment_dict.get('amount_paid'):
            payment_dict['amount_paid'] = int(payment_dict['amount_paid'] * 100)
        
        new_payment = BillPaymentDB(**payment_dict, tenant_id=tenant_id)
        session.add(new_payment)
        # Flush to get the ID without committing
        session.flush()
        
        # 2. Process each allocation
        for allocation_data in allocations:
            # Convert allocated_amount from dollars to cents
            allocated_amount_cents = int(allocation_data.allocated_amount * 100)
            
            # Create allocation with source_id pointing to the payment
            new_allocation = BillPaymentAllocationDB(
                source_id=new_payment.id,
                source_type="payment",
                bill_id=allocation_data.bill_id,
                allocated_amount=allocated_amount_cents,
                allocated_at=allocation_data.allocated_at,
                tenant_id=tenant_id
            )
            session.add(new_allocation)
            
            # 3. Update the bill that receives the allocation
            bill = bill_repository.get_bill_by_id(allocation_data.bill_id, session)
            if not bill:
                raise ValueError(f"Bill {allocation_data.bill_id} not found")
            
            # Update bill amounts (amounts are already in cents in DB)
            bill.amount_paid += allocated_amount_cents
            bill.balance_due = max(0, bill.balance_due - allocated_amount_cents)
            
            # Update payment status
            if bill.balance_due <= 0:
                bill.status = "Closed"
                bill.payment_status = "paid"
            elif bill.amount_paid > 0:
                bill.status = "Partially paid"
                bill.payment_status = "partial"
            
            session.add(bill)  # Add bill to session for update
        
        # 4. Create journal entry if journal_lines are provided
        if journal_lines_data:
            # Use payment_date or current date
            posted_at = payment_data.payment_date if payment_data.payment_date else datetime.utcnow()
            # Use payee_id from payment_data, fallback to reference_id if payee_id is None
            reference_id = payment_data.payee_id if payment_data.payee_id else payment_data.reference_id
            # If both are None, use a default UUID (shouldn't happen in practice, but handle gracefully)
            if not reference_id:
                reference_id = uuid.uuid4()  # Fallback, but this should be set in practice
            
            journal_service.create_journal_for_expense(
                expense_id=new_payment.id,
                expense_type="payment",
                expense_number=payment_data.reference_no,
                reference_id=reference_id,
                posted_at=posted_at,
                tenant_id=tenant_id,
                journal_lines_data=journal_lines_data,
                session=session,
                commit=False
            )
        
        # 5. Commit if requested (otherwise caller handles commit)
        if commit:
            try:
                session.commit()
                session.refresh(new_payment)
            except Exception as e:
                session.rollback()
                raise
        else:
            session.flush()  # Flush to get IDs without committing
            session.refresh(new_payment)
        
        return new_payment
    
    def apply_credit_to_bills(
        self,
        credit_id: uuid.UUID,
        allocations: List[BillPaymentAllocationCreate],
        tenant_id: uuid.UUID,
        session: Session,
        commit: bool = True
    ) -> List[BillPaymentAllocationDB]:
        """
        Apply a vendor credit to bills.
        
        Args:
            credit_id: The vendor credit bill ID
            allocations: List of allocations to bills
            tenant_id: Tenant ID
            session: Database session
            
        Returns:
            List of created allocations
        """
        # Verify the credit exists and is a vendor credit or credit card credit
        # Use get_any_bill_by_id to get vendor credits (which are filtered out by get_bill_by_id)
        credit = bill_repository.get_any_bill_by_id(credit_id, session)
        if not credit:
            raise ValueError(f"Credit {credit_id} not found")
        if credit.bill_rec not in ["vendor_credit", "credit_card_credit"]:
            raise ValueError(f"Bill {credit_id} is not a vendor credit or credit card credit. Found bill_rec='{credit.bill_rec}', expected 'vendor_credit' or 'credit_card_credit'")
        
        created_allocations = []
        
        for allocation_data in allocations:
            # Convert allocated_amount from dollars to cents
            allocated_amount_cents = int(allocation_data.allocated_amount * 100)
            
            # Create allocation with source_id pointing to the credit
            new_allocation = BillPaymentAllocationDB(
                source_id=credit_id,
                source_type="credit",
                bill_id=allocation_data.bill_id,
                allocated_amount=allocated_amount_cents,
                allocated_at=allocation_data.allocated_at,
                tenant_id=tenant_id
            )
            session.add(new_allocation)
            created_allocations.append(new_allocation)
            
            # Update the bill that receives the credit
            bill = bill_repository.get_bill_by_id(allocation_data.bill_id, session)
            if not bill:
                raise ValueError(f"Bill {allocation_data.bill_id} not found")
            
            # Update bill amounts (credits reduce balance, amounts are in cents)
            bill.amount_credited += allocated_amount_cents
            bill.balance_due = max(0, bill.balance_due - allocated_amount_cents)
            
            # Update payment status
            if bill.balance_due <= 0:
                bill.status = "Closed"
                bill.payment_status = "paid"
            elif bill.amount_credited > 0 or bill.amount_paid > 0:
                bill.status = "Partially paid"
                bill.payment_status = "partial"
            
            session.add(bill)  # Add bill to session for update
            
            # Update vendor credit amounts (track how much credit has been used)
            credit.amount_credited += allocated_amount_cents
            credit.balance_due = max(0, credit.balance_due - allocated_amount_cents)
            session.add(credit)  # Explicitly add credit to session to ensure it's updated
        
        # Commit if requested (otherwise caller handles commit)
        if commit:
            try:
                session.commit()
                # Refresh allocations to get their IDs
                for allocation in created_allocations:
                    session.refresh(allocation)
            except Exception as e:
                session.rollback()
                raise
        else:
            session.flush()  # Flush to get IDs without committing
            for allocation in created_allocations:
                session.refresh(allocation)
        
        return created_allocations

    def void_bill_payment(
        self,
        payment_id: uuid.UUID,
        session: Session,
        journal_lines_data: Optional[List[JournalLineCreate]] = None
    ) -> BillPaymentDB:
        """
        Void a bill payment by reversing the journal and optionally creating a new one.
        
        Args:
            payment_id: The bill payment ID to void
            session: Database session
            journal_lines_data: Optional new journal lines to create after reversal
            
        Returns:
            Voided BillPaymentDB instance
        """
        # 1. Get the payment
        payment = bill_payment_repository.get_payment_by_id(payment_id, session)
        if not payment:
            raise ValueError(f"Payment {payment_id} not found")
        
        if payment.status == "void":
            raise ValueError(f"Payment {payment_id} is already voided")
        
        # 2. Find and reverse existing journal entry
        payment_id_str = str(payment.id)
        from app.models.rls.m_journal_header_rls import JournalHeaderDB
        existing_journal_stmt = select(JournalHeaderDB).where(
            JournalHeaderDB.reference == payment_id_str,
            JournalHeaderDB.tenant_id == payment.tenant_id
        )
        existing_journal = session.exec(existing_journal_stmt).first()
        
        if existing_journal:
            # Reverse the existing journal
            reference_id = payment.payee_id if payment.payee_id else payment.reference_id
            if not reference_id:
                reference_id = uuid.uuid4()  # Fallback
            
            journal_service.reverse_journal_for_expense(
                expense_id=payment.id,
                expense_type="payment",
                expense_number=payment.reference_no,
                reference_id=reference_id,
                posted_at=datetime.utcnow(),
                tenant_id=payment.tenant_id,
                existing_journal=existing_journal,
                session=session,
                commit=False
            )
        
        # 3. Create new journal entry if journal_lines are provided
        if journal_lines_data:
            posted_at = payment.payment_date if payment.payment_date else datetime.utcnow()
            reference_id = payment.payee_id if payment.payee_id else payment.reference_id
            if not reference_id:
                reference_id = uuid.uuid4()  # Fallback
            
            journal_service.create_journal_for_expense(
                expense_id=payment.id,
                expense_type="payment",
                expense_number=payment.reference_no,
                reference_id=reference_id,
                posted_at=posted_at,
                tenant_id=payment.tenant_id,
                journal_lines_data=journal_lines_data,
                session=session,
                commit=False
            )
        
        # 4. Set payment status to void
        payment.status = "void"
        payment.updated_at = datetime.utcnow()
        session.add(payment)
        
        # 5. Commit everything in one transaction
        try:
            session.commit()
            session.refresh(payment)
        except Exception as e:
            session.rollback()
            raise
        
        return payment

    def soft_delete_bill_payment(
        self,
        payment_id: uuid.UUID,
        session: Session
    ) -> BillPaymentDB:
        """
        Soft delete a bill payment by reversing the journal and marking it as deleted.
        
        Args:
            payment_id: The bill payment ID to delete
            session: Database session
            
        Returns:
            Deleted BillPaymentDB instance
        """
        # 1. Get the payment
        payment = bill_payment_repository.get_payment_by_id(payment_id, session)
        if not payment:
            raise ValueError(f"Payment {payment_id} not found")
        
        if payment.is_deleted:
            raise ValueError(f"Payment {payment_id} is already deleted")
        
        # 2. Find and reverse existing journal entry
        payment_id_str = str(payment.id)
        from app.models.rls.m_journal_header_rls import JournalHeaderDB
        existing_journal_stmt = select(JournalHeaderDB).where(
            JournalHeaderDB.reference == payment_id_str,
            JournalHeaderDB.tenant_id == payment.tenant_id
        )
        existing_journal = session.exec(existing_journal_stmt).first()
        
        if existing_journal:
            # Reverse the existing journal
            reference_id = payment.payee_id if payment.payee_id else payment.reference_id
            if not reference_id:
                reference_id = uuid.uuid4()  # Fallback
            
            journal_service.reverse_journal_for_expense(
                expense_id=payment.id,
                expense_type="payment",
                expense_number=payment.reference_no,
                reference_id=reference_id,
                posted_at=datetime.utcnow(),
                tenant_id=payment.tenant_id,
                existing_journal=existing_journal,
                session=session,
                commit=False
            )
        
        # 3. Mark payment as deleted
        payment.is_deleted = True
        payment.deleted_at = datetime.utcnow()
        payment.deleted_by = "user"
        session.add(payment)
        
        # 4. Commit everything in one transaction
        try:
            session.commit()
            session.refresh(payment)
        except Exception as e:
            session.rollback()
            raise
        
        return payment


bill_payment_service = BillPaymentService()

