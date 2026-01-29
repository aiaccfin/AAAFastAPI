from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session, select
from app.db.connection.conn_rls import get_tenant_session, tenant_role_session_dependency, tenant_session_dependency
from app.models.rls.m_global_type_rls import TypeDB, TypeCreate, TypeRead, TypeUpdate, TypePatch, TypeDelete, TypeDeleteResponse
import uuid
from app.services.service_global_type import global_type_service

router = APIRouter()
TENANT_ID = "550e8400-e29b-41d4-a716-446655440000"


@router.get("/", response_model=list[TypeRead])
async def list_generic_store(session: Session = Depends(tenant_session_dependency(TENANT_ID))):
    return global_type_service.get_all(session)


@router.post("/", response_model=TypeRead)
async def create_generic(data: TypeCreate,    session: Session = Depends(tenant_session_dependency(TENANT_ID))):

    # Make SQLModel instance
    new_generic = TypeDB(**data.dict(), tenant_id=TENANT_ID)

    session.add(new_generic)
    session.commit()
    session.refresh(new_generic)

    return new_generic



@router.get("/{type_id}", response_model=TypeRead)
async def get_generic(
    type_id: uuid.UUID,
    session: Session = Depends(tenant_session_dependency(TENANT_ID))
):
    """Get a specific global type by ID"""
    type_obj = global_type_service.get_by_id(type_id, session)
    if not type_obj:
        raise HTTPException(status_code=404, detail="Global type not found")
    return type_obj


@router.put("/{type_id}", response_model=TypeRead)
async def update_generic(
    type_id: uuid.UUID,
    data: TypeUpdate,
    session: Session = Depends(tenant_session_dependency(TENANT_ID))
):
    """Update an existing global type (full update - all fields required)"""
    updated = global_type_service.update_type(type_id, data, session)
    if not updated:
        raise HTTPException(status_code=404, detail="Global type not found")
    return updated


@router.patch("/{type_id}", response_model=TypeRead)
async def patch_generic(
    type_id: uuid.UUID,
    data: TypePatch,
    session: Session = Depends(tenant_session_dependency(TENANT_ID))
):
    """Partially update an existing global type (only provided fields are updated)"""
    updated = global_type_service.patch_type(type_id, data, session)
    if not updated:
        raise HTTPException(status_code=404, detail="Global type not found")
    return updated


@router.delete("/{type_id}", response_model=TypeDeleteResponse)
async def delete_generic(
    type_id: uuid.UUID,
    data: TypeDelete,
    session: Session = Depends(tenant_session_dependency(TENANT_ID))
):
    """Soft delete a global type by setting is_deleted, deleted_at, and deleted_by"""
    deleted = global_type_service.soft_delete_type(type_id, data, session)
    if not deleted:
        raise HTTPException(status_code=404, detail="Global type not found")
    return TypeDeleteResponse(id=deleted.id, is_deleted=deleted.is_deleted)

