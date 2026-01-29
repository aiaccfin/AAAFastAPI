# app/services/service_salestax.py
from typing import Optional
from sqlmodel import Session
import uuid
from app.repositories.repository_global_type import global_type_repository
from app.models.rls.m_global_type_rls import TypeDB, TypeUpdate, TypePatch, TypeDelete

class GlobalTypeService:
    def get_all(self, session: Session):
        return global_type_repository.get_all(session)
    
    def get_by_id(self, type_id: uuid.UUID, session: Session) -> Optional[TypeDB]:
        return global_type_repository.get_by_id(type_id, session)
    
    def update_type(
        self,
        type_id: uuid.UUID,
        data: TypeUpdate,
        session: Session
    ) -> Optional[TypeDB]:
        """Full update - all fields required"""
        update_data = data.dict(exclude_unset=False)
        return global_type_repository.update_type(type_id, update_data, session)
    
    def patch_type(
        self,
        type_id: uuid.UUID,
        data: TypePatch,
        session: Session
    ) -> Optional[TypeDB]:
        """Partial update - only provided fields are updated"""
        update_data = data.dict(exclude_unset=True)
        return global_type_repository.update_type(type_id, update_data, session)
    
    def soft_delete_type(
        self,
        type_id: uuid.UUID,
        data: TypeDelete,
        session: Session
    ) -> Optional[TypeDB]:
        """Soft delete by setting is_deleted, deleted_at, and deleted_by"""
        return global_type_repository.soft_delete_type(
            type_id, 
            data.is_deleted,
            session,
            deleted_by=data.deleted_by
        )
    
global_type_service = GlobalTypeService()