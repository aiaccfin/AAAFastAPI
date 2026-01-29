# app/services/service_bill.py
from typing import List, Optional
from sqlmodel import Session, select
from datetime import datetime
import uuid
from app.repositories.repository_bill import bill_repository
from app.models.rls.m_bill_rls import BillDB, BillCreate, BillUpdate, BillRead, BillDelete
from app.models.rls.m_pagination import PaginatedResponse
from app.models.rls.m_journal_header_rls import JournalHeaderDB
from app.services.service_journal import journal_service


class BillService:
    def get_all_bills(self, session: Session) -> List[BillRead]:
        return bill_repository.get_all_bills(session)

    def list_bills(
        self,
        session: Session,
        page: int = 1,
        page_size: int = 20,
        status: Optional[str] = None,
        payment_status: Optional[str] = None,
        issue_date_start: Optional[datetime] = None,
        issue_date_end: Optional[datetime] = None,
    ):
        items, total = bill_repository.get_all(
            session=session,
            page=page,
            page_size=page_size,
            status=status,
            payment_status=payment_status,
            issue_date_start=issue_date_start,
            issue_date_end=issue_date_end,
        )

        total_pages = (total + page_size - 1) // page_size

        return PaginatedResponse(
            items=items,
            total=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages,
            has_next=page < total_pages,
            has_prev=page > 1
        )


    def create_bill(
        self,
        data: BillCreate,
        tenant_id: uuid.UUID,
        session: Session
    ) -> BillDB:
        # Extract journal_lines before creating bill
        journal_lines_data = data.journal_lines or []
        
        # Ensure bill_rec is set to "bill"
        data_dict = data.dict(exclude={"journal_lines"})
        data_dict["bill_rec"] = "bill"
        new_bill = BillDB(**data_dict, tenant_id=tenant_id)
        session.add(new_bill)
        # Flush to get bill.id without committing
        session.flush()
        session.refresh(new_bill)
        
        # Create corresponding journal entry with lines from frontend
        if journal_lines_data:
            journal_service.create_journal_for_expense(
                expense_id=new_bill.id,
                expense_type=new_bill.bill_rec,
                expense_number=new_bill.bill_number,
                reference_id=new_bill.payee_id,
                posted_at=new_bill.issue_date,
                tenant_id=new_bill.tenant_id,
                journal_lines_data=journal_lines_data,
                session=session,
                commit=False
            )
        
        # Commit everything in one transaction
        session.commit()
        session.refresh(new_bill)
        
        return new_bill

    # def create_credit_card_credit(
    #     self,
    #     data: BillCreate,
    #     tenant_id: uuid.UUID,
    #     session: Session
    # ) -> BillDB:
    #     # Extract journal_lines before creating credit
    #     journal_lines_data = data.journal_lines or []
        
    #     data_dict = data.dict(exclude={"journal_lines"})
    #     data_dict["bill_rec"] = "credit_card_credit"
    #     new_credit = BillDB(**data_dict, tenant_id=tenant_id)
    #     session.add(new_credit)
    #     # Flush to get credit.id without committing
    #     session.flush()
    #     session.refresh(new_credit)
        
    #     # Create corresponding journal entry with lines from frontend
    #     if journal_lines_data:
    #         self._create_journal_for_bill(new_credit, journal_lines_data, session, commit=False)
        
    #     # Commit everything in one transaction
    #     session.commit()
    #     session.refresh(new_credit)
        
    #     return new_credit

    def get_bill_by_id(self, bill_id: uuid.UUID, session: Session) -> Optional[BillDB]:
        return bill_repository.get_bill_by_id(bill_id, session)

    def get_bill_by_number(self, bill_number: str, session: Session) -> Optional[BillDB]:
        return bill_repository.get_bill_by_number(bill_number, session)

    def update_bill(self, bill_id: uuid.UUID, data: BillUpdate, session: Session):
        # Use get_any_bill_by_id to support all transaction types (bill, vendor_credit, expense, etc.)
        bill = bill_repository.get_any_bill_by_id(bill_id, session)
        if not bill:
            return None

        # Extract journal_lines before updating bill
        journal_lines_data = getattr(data, 'journal_lines', None)

        # Check if status is being set to "Voided"
        update_data = data.dict(exclude_unset=True, exclude={"journal_lines"})
        is_voiding = update_data.get("status") == "Voided" and bill.status != "Voided"

        # Update bill fields (excluding journal_lines)
        for key, value in update_data.items():
            setattr(bill, key, value)

        # Don't commit yet - wait for journal update
        session.add(bill)
        session.flush()
        session.refresh(bill)

        # If voiding, reverse the existing journal entry
        if is_voiding:
            # Find existing journal entry
            bill_id_str = str(bill.id)
            existing_journal_stmt = select(JournalHeaderDB).where(
                JournalHeaderDB.reference == bill_id_str,
                JournalHeaderDB.tenant_id == bill.tenant_id
            )
            existing_journal = session.exec(existing_journal_stmt).first()
            
            if existing_journal:
                # Reverse the existing journal
                reference_id = bill.payee_id if bill.payee_id else uuid.uuid4()
                posted_at = bill.issue_date if bill.issue_date else datetime.utcnow()
                
                journal_service.reverse_journal_for_expense(
                    expense_id=bill.id,
                    expense_type=bill.bill_rec,
                    expense_number=bill.bill_number,
                    reference_id=reference_id,
                    posted_at=posted_at,
                    tenant_id=bill.tenant_id,
                    existing_journal=existing_journal,
                    session=session,
                    commit=False
                )
        # Update journal entry if journal_lines are provided (and not voiding)
        elif journal_lines_data is not None:
            # Use updated date or original issue_date
            posted_at = bill.issue_date if bill.issue_date else bill.created_at
            journal_service.update_journal_for_expense(
                expense_id=bill.id,
                expense_type=bill.bill_rec,
                expense_number=bill.bill_number,
                reference_id=bill.payee_id,
                posted_at=posted_at,
                tenant_id=bill.tenant_id,
                journal_lines_data=journal_lines_data,
                session=session,
                commit=False
            )

        # Commit everything in one transaction
        session.commit()
        session.refresh(bill)

        return bill

    def get_bills_by_payee(self, session: Session, payee_id: str):
        return bill_repository.get_by_payee_id(session, payee_id)

    def soft_delete_bill(self, bill_id: uuid.UUID, data: BillDelete, session: Session):
        # Use get_any_bill_by_id to support all transaction types (bill, vendor_credit, expense, etc.)
        bill = bill_repository.get_any_bill_by_id(bill_id, session)
        if not bill:
            return None

        # Only reverse journal if actually deleting (is_deleted = True)
        if data.is_deleted:
            # Find and reverse existing journal entry
            bill_id_str = str(bill.id)
            existing_journal_stmt = select(JournalHeaderDB).where(
                JournalHeaderDB.reference == bill_id_str,
                JournalHeaderDB.tenant_id == bill.tenant_id
            )
            existing_journal = session.exec(existing_journal_stmt).first()
            
            if existing_journal:
                # Reverse the existing journal
                reference_id = bill.payee_id if bill.payee_id else uuid.uuid4()
                posted_at = bill.issue_date if bill.issue_date else datetime.utcnow()
                
                journal_service.reverse_journal_for_expense(
                    expense_id=bill.id,
                    expense_type=bill.bill_rec,
                    expense_number=bill.bill_number,
                    reference_id=reference_id,
                    posted_at=posted_at,
                    tenant_id=bill.tenant_id,
                    existing_journal=existing_journal,
                    session=session,
                    commit=False
                )

        bill.is_deleted = data.is_deleted
        bill.deleted_at = datetime.utcnow() if data.is_deleted else None
        bill.deleted_by = "user" if data.is_deleted else None
        session.add(bill)
        
        # Commit everything in one transaction
        try:
            session.commit()
            session.refresh(bill)
        except Exception as e:
            session.rollback()
            raise
        
        return bill


# Service instance
bill_service = BillService()
