from sqlmodel import Session
from typing import List
from app.models.rls.m_journal_header_rls import JournalHeaderDB, JournalHeaderCreate, JournalHeaderRead
from app.repositories.repository_journal import journal_repository


class JournalService:
    def list_all(self, session: Session) -> List[JournalHeaderRead]:
        return journal_repository.get_all(session)

    def create_journal(self, data: JournalHeaderCreate, tenant_id: str, session: Session) -> JournalHeaderDB:
        new_journal = JournalHeaderDB(**data.dict(), tenant_id=tenant_id)
        return journal_repository.save_journal(new_journal, session)


journal_service = JournalService()
