# app/services/service_salestax.py
from sqlmodel import Session
from app.repositories.repository_gst62 import gst62_repository

class GST62Service:
    def list_gst(self, session: Session):
        return gst62_repository.get_all(session)
    
gst62_service = GST62Service()