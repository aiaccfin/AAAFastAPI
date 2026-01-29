# services/service_partner.py
from typing import List, Optional, Dict, Any
import uuid
from requests import session
from sqlmodel import Session
from app.models.rls.m_partner_rls import *
from app.repositories.repository_partner import partner_repository

class PartnerService:

    def list_partners(self, session: Session):
        return partner_repository.get_all(session)

    def get_partner_by_id(self, session: Session, partner_id: uuid.UUID):
        return partner_repository.get_by_id(session, partner_id)

    def get_partners_by_type(self, session: Session, partner_type: PartnerType):
        return partner_repository.get_partners_by_type(session, partner_type)

    def create_partner(self, session: Session, data: PartnerCreate, tenant_id: uuid.UUID):
        return partner_repository.create_partner(session, data, tenant_id)

    def update_partner(self, session: Session, partner_id: uuid.UUID, data: PartnerUpdate):
        partner = partner_repository.get_by_id(session, partner_id)
        if not partner:
            return None

        update_data = data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(partner, field, value)

        return partner_repository.save(session, partner)

    def delete_partner(self, session: Session, partner_id: uuid.UUID):
        return partner_repository.delete(session, partner_id)


partner_service = PartnerService()