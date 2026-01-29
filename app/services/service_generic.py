# app/services/service_salestax.py
from sqlmodel import Session
from app.repositories.repository_generic import generic_repository

class GenericService:
    def get_all(self, session: Session):
        return generic_repository.get_all(session)
    
generic_service = GenericService()