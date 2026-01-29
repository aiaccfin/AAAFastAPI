from typing import List, Dict
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
import uuid

from app.db.connection.conn_rls import tenant_session_dependency
from app.models.rls.m_coa_rls import COACreate, COARead
from app.services.service_coa import coa_service


router = APIRouter()
TENANT_ID = "550e8400-e29b-41d4-a716-446655440000"


@router.get("/", response_model=List[COARead])
async def list_coas(session: Session = Depends(tenant_session_dependency(TENANT_ID))):
    return coa_service.list_all(session)




@router.get("/{coa_id}", response_model=COARead)
async def get_coa(coa_id: uuid.UUID, session: Session = Depends(tenant_session_dependency(TENANT_ID))):
    coa = coa_service.get(session, coa_id)
    if not coa:
        raise HTTPException(status_code=404, detail="COA not found")
    return coa


@router.post("/", response_model=COARead)
async def create_coa(coa_create: COACreate, session: Session = Depends(tenant_session_dependency(TENANT_ID))):
    return coa_service.create(session, TENANT_ID, coa_create)


@router.put("/{coa_id}", response_model=COARead)
async def update_coa(coa_id: uuid.UUID, values: Dict, session: Session = Depends(tenant_session_dependency(TENANT_ID))):
    coa = coa_service.update(session, coa_id, values)
    if not coa:
        raise HTTPException(status_code=404, detail="COA not found")
    return coa


@router.delete("/{coa_id}")
async def delete_coa(coa_id: uuid.UUID, session: Session = Depends(tenant_session_dependency(TENANT_ID))):
    success = coa_service.delete(session, coa_id)
    if not success:
        raise HTTPException(status_code=404, detail="COA not found")
    return {"ok": True}
