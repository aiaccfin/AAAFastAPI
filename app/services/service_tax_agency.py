# app/services/service_tax_agency.py
import uuid
from typing import Optional
from sqlmodel import Session

from app.models.rls.m_gst_agency_rls import (
    TaxAgency,
    TaxAgencyCreate,
    TaxAgencyUpdate,
)

from app.repositories.repository_taxagency import tax_agency_repository


class TaxAgencyService:

    def list_agencies(self, session: Session):
        return tax_agency_repository.get_all(session)

    def get_agency(self, agency_id: uuid.UUID, session: Session) -> Optional[TaxAgency]:
        return tax_agency_repository.get_by_id(agency_id, session)

    def create_agency(self, data: TaxAgencyCreate, tenant_id: str, session: Session) -> TaxAgency:
        new_agency = TaxAgency(**data.dict(),  tenant_id=tenant_id)
        return tax_agency_repository.save(new_agency, session)

    def update_agency(self, agency_id: uuid.UUID, data: TaxAgencyCreate, session: Session):
        agency = tax_agency_repository.get_by_id(agency_id, session)
        if not agency:
            return None

        update_data = data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(agency, field, value)

        return tax_agency_repository.save(agency, session)

    def delete_agency(self, agency_id: uuid.UUID, session: Session):
        return tax_agency_repository.delete(agency_id, session)


tax_agency_service = TaxAgencyService()
