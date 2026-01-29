# app/repositories/gst_repository.py
from typing import Optional
from datetime import datetime
from sqlmodel import Session, select
from app.models.rls.m_global_type_rls import TypeDB
import uuid

class GlobalTypeRepository:
    def get_all(self, session: Session):
        statement = select(TypeDB).where(TypeDB.is_deleted.isnot(True))
        return session.exec(statement).all()
    
    def get_by_id(self, type_id: uuid.UUID, session: Session) -> Optional[TypeDB]:
        statement = select(TypeDB).where(TypeDB.id == type_id)
        return session.exec(statement).first()
    
    def update_type(
        self,
        type_id: uuid.UUID,
        update_data: dict,
        session: Session
    ) -> Optional[TypeDB]:
        db_type = self.get_by_id(type_id, session)
        if not db_type:
            return None
        
        for field, value in update_data.items():
            if hasattr(db_type, field):
                setattr(db_type, field, value)
        
        db_type.updated_at = datetime.utcnow()
        session.add(db_type)
        session.commit()
        session.refresh(db_type)
        return db_type
    
    def soft_delete_type(
        self,
        type_id: uuid.UUID,
        is_deleted: bool,
        session: Session,
        deleted_by: Optional[str] = None
    ) -> Optional[TypeDB]:
        """Soft delete by setting is_deleted, deleted_at, and deleted_by"""
        db_type = self.get_by_id(type_id, session)
        if not db_type:
            return None
        
        db_type.is_deleted = is_deleted
        if is_deleted:
            db_type.deleted_at = datetime.utcnow()
            db_type.deleted_by = deleted_by or "system"
        else:
            # Restore: clear deletion fields
            db_type.deleted_at = None
            db_type.deleted_by = None
        db_type.updated_at = datetime.utcnow()
        session.add(db_type)
        session.commit()
        session.refresh(db_type)
        return db_type

global_type_repository = GlobalTypeRepository()