from typing import Optional
import uuid
from sqlmodel import Session, select
from app.models.rls.m_coa_rls import COADB

class COARepository:
    def get_all(self, session: Session):
        statement = select(COADB)
        return session.exec(statement).all()

    # def get_all(self, session: Session):
    #     # select only columns to avoid lazy-loading parent/children
    #     statement = select(
    #         COADB.id,
    #         COADB.code,
    #         COADB.name,
    #         COADB.type,
    #         COADB.currency,
    #         COADB.extras,
    #         COADB.parent_id
    #     )
    #     return session.exec(statement).all()

    def get_by_id(self, session: Session, coa_id: uuid.UUID) -> Optional[COADB]:
        statement = select(COADB).where(COADB.id == coa_id)
        return session.exec(statement).first()

    def get_by_code(self, session: Session, code: str) -> Optional[COADB]:
        statement = select(COADB).where(COADB.code == code)
        return session.exec(statement).first()

    def create(self, session: Session, coa: COADB) -> COADB:
        session.add(coa)
        session.commit()
        session.refresh(coa)
        return coa

    def update(self, session: Session, coa: COADB, values: dict) -> COADB:
        for key, value in values.items():
            setattr(coa, key, value)
        session.add(coa)
        session.commit()
        session.refresh(coa)
        return coa

    def delete(self, session: Session, coa: COADB):
        session.delete(coa)
        session.commit()

# Singleton instance
coa_repository = COARepository()
