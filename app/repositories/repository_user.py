# app/repositories/gst_repository.py
from sqlmodel import Session, select
from app.models.rls.m_user_rls import UserTable

class UserRepository:
    def get_all(self, session: Session):
        statement = select(UserTable)
        return session.exec(statement).all()

user_repository = UserRepository()