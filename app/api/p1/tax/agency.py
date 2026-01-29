from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session
import uuid

from app.db.connection.conn_rls import tenant_session_dependency
from app.models.rls.m_gst_agency_rls import (
    TaxAgency,
    TaxAgencyCreate,
    TaxAgencyRead,
    TaxAgencyUpdate,
)

from app.services.service_tax_agency import tax_agency_service


router = APIRouter()
TENANT_ID = "550e8400-e29b-41d4-a716-446655440000"


@router.get("", response_model=List[TaxAgencyRead])
async def list_tax_agencies(session: Session = Depends(tenant_session_dependency(TENANT_ID))):
    return tax_agency_service.list_agencies(session)


@router.get("/{agency_id}", response_model=TaxAgencyRead)
async def get_tax_agency(
    agency_id: uuid.UUID,
    session: Session = Depends(tenant_session_dependency(TENANT_ID))
):
    agency = tax_agency_service.get_agency(agency_id, session)
    if not agency:
        raise HTTPException(status_code=404, detail="Tax agency not found")
    return agency


@router.post("", response_model=TaxAgencyRead)
async def create_tax_agency(
    data: TaxAgencyCreate,
    session: Session = Depends(tenant_session_dependency(TENANT_ID))
):
    return tax_agency_service.create_agency(data, TENANT_ID, session)


@router.patch("/{agency_id}", response_model=TaxAgencyRead)
async def update_tax_agency(
    agency_id: uuid.UUID,
    data: TaxAgencyUpdate,
    session: Session = Depends(tenant_session_dependency(TENANT_ID))
):
    updated = tax_agency_service.update_agency(agency_id, data, session)
    if not updated:
        raise HTTPException(status_code=404, detail="Tax agency not found")
    return updated


@router.delete("/{agency_id}")
async def delete_tax_agency(
    agency_id: uuid.UUID,
    session: Session = Depends(tenant_session_dependency(TENANT_ID))
):
    deleted = tax_agency_service.delete_agency(agency_id, session)
    if not deleted:
        raise HTTPException(status_code=404, detail="Tax agency not found")
    return {"deleted": True}
