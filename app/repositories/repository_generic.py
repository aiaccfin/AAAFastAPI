# app/repositories/gst_repository.py
from sqlmodel import Session, select
from app.models.rls.m_generic_rls import GenericStore

class GenericRepository:
    def get_all(self, session: Session):
        statement = select(GenericStore)
        return session.exec(statement).all()

generic_repository = GenericRepository()