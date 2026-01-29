# endpoints/partner.py
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session
from typing import List, Optional
import uuid

from app.db.connection.conn_rls import tenant_session_dependency
from app.models.rls.m_partner_rls import Partner, PartnerCreate, PartnerUpdate, PartnerResponse, PartnerBrief, PartnerType
from app.services.service_partner import partner_service

router = APIRouter()

# These would come from your auth system
TENANT_ID = "550e8400-e29b-41d4-a716-446655440000"
ROLE_ID = "112"
USER_ID = "111"


@router.get("/", response_model=list[PartnerBrief], description="List all partners for the tenant")
async def list_partners(session: Session = Depends(tenant_session_dependency(TENANT_ID))):
    return partner_service.list_partners(session)


@router.post("/", response_model=PartnerResponse)
async def create_partner(
    data: PartnerCreate,
    session: Session = Depends(tenant_session_dependency(TENANT_ID))
):
    return partner_service.create_partner(session, data, TENANT_ID)


@router.get("/{partner_id}", response_model=PartnerResponse)
async def get_partner(
    partner_id: uuid.UUID,
    session: Session = Depends(tenant_session_dependency(TENANT_ID))
):
    partner = partner_service.get_partner_by_id(session, partner_id)
    if not partner:
        raise HTTPException(status_code=404, detail="Partner not found")
    return partner



@router.get("/type/{partner_type}", response_model=List[PartnerBrief])
async def list_partners_by_type(
    partner_type: PartnerType,
    session: Session = Depends(tenant_session_dependency(TENANT_ID))
):
    return partner_service.get_partners_by_type(session, partner_type, TENANT_ID)


@router.get("/search/", response_model=List[PartnerBrief])
async def search_partners(
    name: Optional[str] = Query(None, min_length=1),
    session: Session = Depends(tenant_session_dependency(TENANT_ID))
):
    return partner_service.search_partners_by_name(session, name, TENANT_ID)


@router.delete("/{partner_id}", response_model=dict)
async def delete_partner(
    partner_id: uuid.UUID,
    session: Session = Depends(tenant_session_dependency(TENANT_ID))
):
    success = partner_service.delete_partner(session, partner_id)
    if not success:
        raise HTTPException(status_code=404, detail="Partner not found")
    return {"detail": "Partner deleted successfully"}
