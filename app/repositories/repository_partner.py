# app/repositories/gst_repository.py
from sqlmodel import Session, select
from app.models.rls.m_partner_rls import Partner, PartnerType, PartnerCreate, PartnerUpdate
from typing import List, Optional, Dict, Any
from datetime import datetime
import uuid


class PartnerRepository:
    def get_all(self, session: Session):
        statement = select(Partner)
        return session.exec(statement).all()

    def get_partners_by_type(self,  session: Session, partner_type: PartnerType) -> List[Partner]:
        statement = select(Partner).where(
            (Partner.type == partner_type)
        )
        return session.exec(statement).all()

    def get_by_id(self,  session: Session, partner_id: str):
        return session.get(Partner, partner_id)

    def create_partner(
        self,
        session: Session,
        partner_data: PartnerCreate,
        tenant_id: uuid.UUID
    ) -> Partner:
        db_partner = Partner(**partner_data.dict(), tenant_id=tenant_id)
        session.add(db_partner)
        session.commit()
        session.refresh(db_partner)
        return db_partner

    def save(self, partner: Partner, session: Session):
        session.add(partner)
        session.commit()
        session.refresh(partner)
        return partner

    # def save(self, partner: Partner, session: Session) -> Partner:
    #         """Persist changes to DB"""
    #         session.add(partner)
    #         session.commit()
    #         session.refresh(partner)
    #         return partner

    def update_partner(self, partner_id: uuid.UUID, partner_data: PartnerUpdate, tenant_id: uuid.UUID) -> Optional[Partner]:
        db_partner = self.get_partner_by_id(partner_id, tenant_id)
        if not db_partner:
            return None

        # Update only provided fields
        update_data = partner_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            if hasattr(db_partner, field):
                setattr(db_partner, field, value)

        db_partner.updated_at = datetime.utcnow()
        self.session.add(db_partner)
        self.session.commit()
        self.session.refresh(db_partner)
        return db_partner

    def update_partner_status(self, partner_id: uuid.UUID, status: str, tenant_id: uuid.UUID) -> Optional[Partner]:
        db_partner = self.get_partner_by_id(partner_id, tenant_id)
        if db_partner:
            db_partner.status = status
            db_partner.updated_at = datetime.utcnow()
            self.session.add(db_partner)
            self.session.commit()
            self.session.refresh(db_partner)
        return db_partner

    def add_partner_note(self, partner_id: uuid.UUID, note_data: Dict[str, Any], tenant_id: uuid.UUID) -> Optional[Partner]:
        db_partner = self.get_partner_by_id(partner_id, tenant_id)
        if db_partner:
            new_note = {
                "id": str(uuid.uuid4()),
                "message": note_data.get("message", ""),
                "attachments": note_data.get("attachments", []),
                "commenter_id": note_data.get("commenter_id"),
                "comment_post_time": datetime.utcnow().isoformat(),
                "is_edited": False
            }
            db_partner.notes.append(new_note)
            db_partner.updated_at = datetime.utcnow()
            self.session.add(db_partner)
            self.session.commit()
            self.session.refresh(db_partner)
        return db_partner

    # ... other methods with tenant_id parameter
partner_repository = PartnerRepository()
