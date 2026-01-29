# app/services/service_credit_card_credit.py
from typing import Optional
from sqlmodel import Session, text
from datetime import datetime
import uuid
from app.repositories.repository_credit_card_credit import credit_card_credit_repository
from app.models.rls.m_bill_rls import BillDB, BillCreate, BillUpdate
from app.models.rls.m_pagination import PaginatedResponse
from app.services.service_journal import journal_service


class CreditCardCreditService:
    def list_credits(
        self,
        session: Session,
        page: int = 1,
        page_size: int = 20,
        status: Optional[str] = None,
        payment_status: Optional[str] = None,
        issue_date_start: Optional[datetime] = None,
        issue_date_end: Optional[datetime] = None,
    ):
        items, total = credit_card_credit_repository.get_all(
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

    def create_credit(
        self,
        data: BillCreate,
        tenant_id: uuid.UUID,
        session: Session
    ) -> BillDB:
        # Extract journal_lines before creating credit
        journal_lines_data = data.journal_lines or []
        
        data_dict = data.dict(exclude={"journal_lines"})
        data_dict["bill_rec"] = "credit_card_credit"
        new_credit = BillDB(**data_dict, tenant_id=tenant_id)
        session.add(new_credit)
        # Flush to get credit.id without committing
        session.flush()
        session.refresh(new_credit)
        
        # Create corresponding journal entry with lines from frontend
        if journal_lines_data:
            journal_service.create_journal_for_expense(
                expense_id=new_credit.id,
                expense_type=new_credit.bill_rec,
                expense_number=new_credit.bill_number,
                reference_id=new_credit.payee_id,
                posted_at=new_credit.issue_date,
                tenant_id=new_credit.tenant_id,
                journal_lines_data=journal_lines_data,
                session=session,
                commit=False
            )
        
        # Commit everything in one transaction
        session.commit()
        session.refresh(new_credit)
        
        return new_credit

    # def get_next_credit_number_for_me(self, db: Session, tenant_id: uuid.UUID) -> int:
    #     stmt = text("SELECT next_bill_number(:tenant_id)")
    #     result = db.exec(stmt, params={"tenant_id": str(tenant_id)})
    #     db.commit()
    #     return result.scalar_one()

    def get_credit_by_id(self, credit_id: uuid.UUID, session: Session) -> Optional[BillDB]:
        return credit_card_credit_repository.get_credit_by_id(credit_id, session)

    def get_credit_by_number(self, credit_number: str, session: Session) -> Optional[BillDB]:
        return credit_card_credit_repository.get_credit_by_number(credit_number, session)

    def update_credit(self, credit_id: uuid.UUID, data: BillUpdate, session: Session):
        credit = credit_card_credit_repository.get_credit_by_id(credit_id, session)
        if not credit:
            return None

        update_data = data.dict(exclude_unset=True)

        for key, value in update_data.items():
            setattr(credit, key, value)

        updated_credit = credit_card_credit_repository.update_credit(session, credit)
        return updated_credit

    def get_credits_by_payee(self, session: Session, payee_id: str):
        return credit_card_credit_repository.get_by_payee_id(session, payee_id)


credit_card_credit_service = CreditCardCreditService()

