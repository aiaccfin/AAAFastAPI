# app/services/service_expense.py
from typing import List, Optional
from sqlmodel import Session, text
from datetime import datetime
import uuid
from app.repositories.repository_expense import expense_repository
from app.models.rls.m_bill_rls import BillDB, BillCreate, BillUpdate
from app.models.rls.m_pagination import PaginatedResponse
from app.services.service_journal import journal_service


class ExpenseService:
    def list_expenses(
        self,
        session: Session,
        page: int = 1,
        page_size: int = 20,
        status: Optional[str] = None,
        payment_status: Optional[str] = None,
        issue_date_start: Optional[datetime] = None,
        issue_date_end: Optional[datetime] = None,
    ):
        items, total = expense_repository.get_all(
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

    def create_expense(
        self,
        data: BillCreate,
        tenant_id: uuid.UUID,
        session: Session
    ) -> BillDB:
        # Extract journal_lines before creating expense
        journal_lines_data = data.journal_lines or []
        
        data_dict = data.dict(exclude={"journal_lines"})
        data_dict["bill_rec"] = "expense"
        new_expense = BillDB(**data_dict, tenant_id=tenant_id)
        session.add(new_expense)
        # Flush to get expense.id without committing
        session.flush()
        session.refresh(new_expense)
        
        # Create corresponding journal entry with lines from frontend
        if journal_lines_data:
            journal_service.create_journal_for_expense(
                expense_id=new_expense.id,
                expense_type=new_expense.bill_rec,
                expense_number=new_expense.bill_number,
                reference_id=new_expense.payee_id,
                posted_at=new_expense.issue_date,
                tenant_id=new_expense.tenant_id,
                journal_lines_data=journal_lines_data,
                session=session,
                commit=False
            )
        
        # Commit everything in one transaction
        session.commit()
        session.refresh(new_expense)
        
        return new_expense

    # def get_next_expense_number_for_me(self, db: Session, tenant_id: uuid.UUID) -> int:
    #     stmt = text("SELECT next_bill_number(:tenant_id)")
    #     result = db.exec(stmt, params={"tenant_id": str(tenant_id)})
    #     db.commit()
    #     return result.scalar_one()

    def get_expense_by_id(self, expense_id: uuid.UUID, session: Session) -> Optional[BillDB]:
        return expense_repository.get_expense_by_id(expense_id, session)

    def get_expense_by_number(self, expense_number: str, session: Session) -> Optional[BillDB]:
        return expense_repository.get_expense_by_number(expense_number, session)

    def update_expense(self, expense_id: uuid.UUID, data: BillUpdate, session: Session):
        expense = expense_repository.get_expense_by_id(expense_id, session)
        if not expense:
            return None

        update_data = data.dict(exclude_unset=True)

        for key, value in update_data.items():
            setattr(expense, key, value)

        updated_expense = expense_repository.update_expense(session, expense)
        return updated_expense

    def get_expenses_by_payee(self, session: Session, payee_id: str):
        return expense_repository.get_by_payee_id(session, payee_id)


expense_service = ExpenseService()

