from sqlmodel import Session, select
from app.models.rls.m_journal_header_rls import JournalHeaderDB


class JournalRepository:
    def get_all(self, session: Session):
        statement = select(JournalHeaderDB)
        return session.exec(statement).all()


    def save_journal(self, journal: JournalHeaderDB, session: Session) -> JournalHeaderDB:
        session.add(journal)
        session.commit()
        session.refresh(journal)
        return journal
   

journal_repository = JournalRepository()
