import datetime
from typing import List
import uuid
from fastapi import APIRouter, Depends
from sqlmodel import Session

from app.db.connection.conn_rls import tenant_session_dependency
from app.services.service_journal import journal_service
from app.models.rls.m_journal_header_rls import JournalHeaderDB, JournalHeaderRead, JournalHeaderCreate
from app.models.rls.m_journal_line_rls import JournalLineDB, JournalLineCreate,     JournalLineRead

router = APIRouter()
TENANT_ID = "550e8400-e29b-41d4-a716-446655440000"


@router.get("/", response_model=List[JournalHeaderRead])
async def list_journals(session: Session = Depends(tenant_session_dependency(TENANT_ID))):
    return journal_service.list_all(session)

@router.post("/header", response_model=JournalHeaderRead)
async def create_journal(data: JournalHeaderCreate, session: Session = Depends(tenant_session_dependency(TENANT_ID))):
    new_journal = journal_service.create_journal(data, TENANT_ID, session)
    return new_journal

@router.post("/lines", response_model=JournalLineRead)
async def create_journal(data: JournalLineCreate, session: Session = Depends(tenant_session_dependency(TENANT_ID))):
    new_journal = journal_service.create_journal_lines(data, TENANT_ID, session)
    return new_journal

@router.post("/", response_model=JournalHeaderRead)
async def create_journal(data: JournalHeaderCreate, session: Session = Depends(tenant_session_dependency(TENANT_ID))):
    new_journal = journal_service.create_journal(data, TENANT_ID, session)

    # 2️⃣ Create lines
    created_lines = []
    for line in getattr(data, "journal_lines", []):
        line_db = JournalLineDB(
            journal_id=new_journal.id,
            account_id=line.account_id,
            debit=line.debit,
            credit=line.credit,
            extras=line.extras,
            tenant_id=new_journal.tenant_id
        )
        session.add(line_db)
        created_lines.append(line_db)

    session.commit()
    for line in created_lines:
        session.refresh(line)  # get generated id

    # 3️⃣ Attach lines to header object
    new_journal.journal_lines = created_lines

    return new_journal
