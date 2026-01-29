# app/repositories/repository_expense.py
from datetime import datetime
from typing import Optional
import uuid
from sqlmodel import Session, func, select
from app.models.rls.m_bill_rls import BillDB


class ExpenseRepository:
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
        base_stmt = select(BillDB).where(
            BillDB.is_deleted.isnot(True),
            BillDB.bill_rec == "expense"
        )

        if status:
            base_stmt = base_stmt.where(BillDB.status == status)

        if payment_status:
            base_stmt = base_stmt.where(BillDB.payment_status == payment_status)

        if issue_date_start:
            base_stmt = base_stmt.where(BillDB.issue_date >= issue_date_start)

        if issue_date_end:
            base_stmt = base_stmt.where(BillDB.issue_date <= issue_date_end)

        count_stmt = select(func.count()).select_from(base_stmt.subquery())
        total = session.exec(count_stmt).one()

        stmt = base_stmt.offset((page - 1) * page_size).limit(page_size)
        items = session.exec(stmt).all()

        return items, total

    def get_expense_by_id(self, expense_id: str | uuid.UUID, session: Session) -> BillDB | None:
        statement = select(BillDB).where(
            BillDB.id == expense_id,
            BillDB.bill_rec == "expense"
        )
        return session.exec(statement).first()

    def get_expense_by_number(self, expense_number: str, session: Session) -> BillDB | None:
        try:
            sequence = int(expense_number.split('-')[-1])
        except ValueError:
            return None

        statement = select(BillDB).where(
            BillDB.bill_sequence == sequence,
            BillDB.bill_rec == "expense"
        )
        return session.exec(statement).first()

    def save_expense(self, expense: BillDB, session: Session) -> BillDB:
        session.add(expense)
        session.commit()
        session.refresh(expense)
        return expense

    def update_expense(self, session: Session, expense: BillDB) -> BillDB:
        session.add(expense)
        session.commit()
        session.refresh(expense)
        return expense

    def get_by_payee_id(self, session: Session, payee_id: str):
        statement = (
            select(BillDB)
            .where(
                BillDB.payee_id == payee_id,
                BillDB.bill_rec == "expense"
            )
            .order_by(BillDB.created_at.desc())
        )
        return session.exec(statement).all()


expense_repository = ExpenseRepository()

