# app/services/service_salestax.py
import uuid
from sqlmodel import Session
from typing import List, Optional

from app.repositories.repository_coa import coa_repository
from app.models.rls.m_coa_rls import COACreate, COARead, COADB

class COAService:
    # def list_all(self, session: Session) -> List[COARead]:
    #     coas = coa_repository.get_all(session)
    #     return [COARead.from_orm(c) for c in coas]

    def list_all(self, session: Session):
        return coa_repository.get_all(session)


    def get_all(self, session: Session) -> List[COARead]:
        coas = coa_repository.get_all(session)
        return [COARead.from_orm(c) for c in coas]

    def get(self, session: Session, coa_id: uuid.UUID) -> Optional[COARead]:
        coa = coa_repository.get_by_id(session, coa_id)
        if coa:
            return COARead.from_orm(coa)
        return None

    def create(self, session: Session, tenant_id: uuid.UUID, coa_create: COACreate) -> COARead:
        coa_db = COADB(**coa_create.dict(), tenant_id=tenant_id)
        coa_db.id = uuid.uuid4()
        coa = coa_repository.create(session, coa_db)
        return COARead.from_orm(coa)

    def update(self, session: Session, coa_id: uuid.UUID, values: dict) -> Optional[COARead]:
        coa = coa_repository.get_by_id(session, coa_id)
        if not coa:
            return None
        coa = coa_repository.update(session, coa, values)
        return COARead.from_orm(coa)

    def delete(self, session: Session, coa_id: uuid.UUID) -> bool:
        coa = coa_repository.get_by_id(session, coa_id)
        if not coa:
            return False
        coa_repository.delete(session, coa)
        return True


# Singleton instance
coa_service = COAService()
