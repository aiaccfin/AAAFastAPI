# app/repositories/tax_agency_repository.py
from sqlmodel import Session, select
from app.models.rls.m_gst_agency_rls import TaxAgency


class TaxAgencyRepository:

    def get_all(self, session: Session):
        statement = select(TaxAgency)
        return session.exec(statement).all()

    def get_by_id(self, agency_id: str, session: Session):
        return session.get(TaxAgency, agency_id)

    def save(self, obj: TaxAgency, session: Session):
        session.add(obj)
        session.commit()
        session.refresh(obj)
        return obj

    def delete(self, agency_id: str, session: Session):
        obj = session.get(TaxAgency, agency_id)
        if obj:
            session.delete(obj)
            session.commit()
        return obj


tax_agency_repository = TaxAgencyRepository()
