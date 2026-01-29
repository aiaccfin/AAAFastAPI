# app/repositories/gst_repository.py
from sqlmodel import Session, select
from app.models.rls.m_gst_rls import GSTTable

class GST62Repository:
    def get_all(self, session: Session):
        statement = select(GSTTable)
        return session.exec(statement).all()

gst62_repository = GST62Repository()