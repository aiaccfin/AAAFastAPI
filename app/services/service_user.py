# app/services/service_salestax.py
from sqlmodel import Session
from app.repositories.repository_user import user_repository

class UserService:
    def list_users(self, session: Session):
        return user_repository.get_all(session)
    
user_service = UserService()