# app/repositories/repository_bill.py
from datetime import datetime
from typing import Optional
import uuid
from sqlmodel import Session, func, select
from app.models.rls.m_bill_rls import BillDB


class BillRepository:
    def get_all(
        self,
        session: Session,
        page: int,
        page_size: int,
        status: Optional[str] = None,
        payment_status: Optional[str] = None,
        issue_date_start: Optional[datetime] = None,
        issue_date_end: Optional[datetime] = None,
    ):
        # base - filter by bill_rec = "bill"
        base_stmt = select(BillDB).where(
            BillDB.is_deleted.isnot(True),
            BillDB.bill_rec == "bill"
        )

        # status filter
        if status:
            base_stmt = base_stmt.where(BillDB.status == status)

        # payment_status filter
        if payment_status:
            base_stmt = base_stmt.where(BillDB.payment_status == payment_status)

        # date filters
        if issue_date_start:
            base_stmt = base_stmt.where(BillDB.issue_date >= issue_date_start)

        if issue_date_end:
            base_stmt = base_stmt.where(BillDB.issue_date <= issue_date_end)

        # count total
        count_stmt = select(func.count()).select_from(base_stmt.subquery())
        total = session.exec(count_stmt).one()

        # pagination
        stmt = base_stmt.offset((page - 1) * page_size).limit(page_size)
        items = session.exec(stmt).all()

        return items, total

    def get_all_bills(self, session: Session):
        statement = (
            select(BillDB)
            .where(BillDB.is_deleted.isnot(True))
            .order_by(BillDB.created_at.desc())
        )
        return session.exec(statement).all()

    def get_bill_by_id(self, bill_id: str | uuid.UUID, session: Session, bill_rec: str | None = "bill") -> BillDB | None:
        """
        Get a bill by ID.
        
        Args:
            bill_id: The bill ID
            session: Database session
            bill_rec: Optional filter by bill_rec type. If None, returns any bill type.
        """
        statement = select(BillDB).where(BillDB.id == bill_id)
        if bill_rec is not None:
            statement = statement.where(BillDB.bill_rec == bill_rec)
        return session.exec(statement).first()
    
    def get_any_bill_by_id(self, bill_id: str | uuid.UUID, session: Session) -> BillDB | None:
        """Get any bill by ID regardless of bill_rec type"""
        return self.get_bill_by_id(bill_id, session, bill_rec=None)

    def get_bill_by_number(self, bill_number: str, session: Session) -> BillDB | None:
        statement = select(BillDB).where(
            BillDB.bill_number == bill_number,
            BillDB.bill_rec == "bill"
        )
        return session.exec(statement).first()

    def save_bill(self, bill: BillDB, session: Session) -> BillDB:
        session.add(bill)
        session.commit()
        session.refresh(bill)
        return bill

    def update_bill(self, session: Session, bill: BillDB) -> BillDB:
        session.add(bill)
        session.commit()
        session.refresh(bill)
        return bill

    def get_by_payee_id(self, session: Session, payee_id: str):
        statement = (
            select(BillDB)
            .where(
                BillDB.payee_id == payee_id,
                BillDB.bill_rec == "bill"
            )
            .order_by(BillDB.created_at.desc())
        )
        return session.exec(statement).all()


bill_repository = BillRepository()
