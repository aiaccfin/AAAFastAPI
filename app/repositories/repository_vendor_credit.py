# app/repositories/repository_vendor_credit.py
from datetime import datetime
from typing import Optional
import uuid
from sqlmodel import Session, func, select
from app.models.rls.m_bill_rls import BillDB


class VendorCreditRepository:
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
        # base - filter by bill_rec = "vendor_credit"
        base_stmt = select(BillDB).where(
            BillDB.is_deleted.isnot(True),
            BillDB.bill_rec == "vendor_credit"
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

    def get_vendor_credit_by_id(self, vendor_credit_id: str | uuid.UUID, session: Session) -> BillDB | None:
        statement = select(BillDB).where(
            BillDB.id == vendor_credit_id,
            BillDB.bill_rec == "vendor_credit"
        )
        return session.exec(statement).first()

    def get_vendor_credit_by_number(self, vendor_credit_number: str, session: Session) -> BillDB | None:
        # Extract sequence number from vendor credit formats like "VC-1001" or "1001"
        try:
            sequence = int(vendor_credit_number.split('-')[-1])
        except ValueError:
            return None

        statement = select(BillDB).where(
            BillDB.bill_sequence == sequence,
            BillDB.bill_rec == "vendor_credit"
        )
        return session.exec(statement).first()

    def save_vendor_credit(self, vendor_credit: BillDB, session: Session) -> BillDB:
        session.add(vendor_credit)
        session.commit()
        session.refresh(vendor_credit)
        return vendor_credit

    def update_vendor_credit(self, session: Session, vendor_credit: BillDB) -> BillDB:
        session.add(vendor_credit)
        session.commit()
        session.refresh(vendor_credit)
        return vendor_credit

    def get_by_payee_id(self, session: Session, payee_id: str):
        statement = (
            select(BillDB)
            .where(
                BillDB.payee_id == payee_id,
                BillDB.bill_rec == "vendor_credit"
            )
            .order_by(BillDB.created_at.desc())
        )
        return session.exec(statement).all()


vendor_credit_repository = VendorCreditRepository()

