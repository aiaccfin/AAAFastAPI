from sqlmodel import Session, select
from typing import List, Optional
from datetime import datetime
import uuid
from app.models.rls.m_journal_header_rls import JournalHeaderDB, JournalHeaderCreate, JournalHeaderRead
from app.models.rls.m_journal_line_rls import JournalLineDB, JournalLineCreate
from app.repositories.repository_journal import journal_repository


class JournalService:
    def list_all(self, session: Session) -> List[JournalHeaderRead]:
        return journal_repository.get_all(session)

    def create_journal(self, data: JournalHeaderCreate, tenant_id: str, session: Session) -> JournalHeaderDB:
        new_journal = JournalHeaderDB(**data.dict(), tenant_id=tenant_id)
        return journal_repository.save_journal(new_journal, session)

    def create_journal_with_lines(
        self, 
        data: JournalHeaderCreate, 
        tenant_id: uuid.UUID, 
        session: Session,
        commit: bool = True
    ) -> JournalHeaderDB:
        """
        Create a journal header and its associated journal lines in a single transaction.
        
        Args:
            data: JournalHeaderCreate containing header data and optional journal_lines
            tenant_id: Tenant UUID
            session: Database session
            commit: Whether to commit the transaction (default True, set False for single transaction)
            
        Returns:
            JournalHeaderDB with created journal lines
        """
        # Convert tenant_id to UUID if it's a string
        if isinstance(tenant_id, str):
            tenant_id = uuid.UUID(tenant_id)
        
        # Extract journal_lines from data before creating header
        journal_lines_data = data.journal_lines or []
        
        # Create header (excluding journal_lines from dict)
        header_dict = data.dict(exclude={"journal_lines"})
        new_journal = JournalHeaderDB(**header_dict, tenant_id=tenant_id)
        session.add(new_journal)
        # Flush to get the ID without committing
        session.flush()
        session.refresh(new_journal)
        
        # Create journal lines
        created_lines = []
        for line_data in journal_lines_data:
            line_db = JournalLineDB(
                journal_header_id=new_journal.id,
                account_id=line_data.account_id,
                debit=line_data.debit,
                credit=line_data.credit,
                extras=line_data.extras,
                tenant_id=tenant_id
            )
            session.add(line_db)
            created_lines.append(line_db)
        
        # Only commit if requested (for single transaction, parent will commit)
        if commit:
            session.commit()
            for line in created_lines:
                session.refresh(line)
        else:
            # Flush to ensure IDs are available
            session.flush()
            for line in created_lines:
                session.refresh(line)
        
        return new_journal

    def create_journal_for_expense(
        self,
        expense_id: uuid.UUID,
        expense_type: str,
        expense_number: Optional[str],
        reference_id: uuid.UUID,
        posted_at: datetime,
        tenant_id: uuid.UUID,
        journal_lines_data: List[JournalLineCreate],
        session: Session,
        commit: bool = True
    ) -> JournalHeaderDB:
        """
        Create a journal entry for an expense transaction (bill, vendor credit, credit card credit, payment, etc.).
        This is a generic method that can be used for all expense-related transactions.
        
        Args:
            expense_id: The ID of the expense transaction (bill_id, payment_id, etc.)
            expense_type: Type of expense (bill, vendor_credit, credit_card_credit, payment, etc.)
            expense_number: Optional reference number (bill_number, payment_number, etc.)
            reference_id: ID of related entity (payee_id, vendor_id, etc.)
            posted_at: Date when the transaction was posted
            tenant_id: Tenant UUID
            journal_lines_data: Journal lines from frontend
            session: Database session
            commit: Whether to commit the transaction (default True, set False for single transaction)
            
        Returns:
            JournalHeaderDB - The created journal header
        """
        # Add expense reference to each journal line's extras
        # Note: journal_header_id will be set by backend after creating journal header
        journal_lines = []
        for line in journal_lines_data:
            line_extras = line.extras.copy() if line.extras else {}
            line_extras.update({
                f"{expense_type}_id": str(expense_id),
                f"{expense_type}_number": expense_number
            })
            # Create journal line without journal_header_id (will be set by backend)
            journal_lines.append(
                JournalLineCreate(
                    account_id=line.account_id,
                    debit=line.debit,
                    credit=line.credit,
                    extras=line_extras,
                    journal_header_id=None  # Explicitly set to None - backend will assign after header creation
                )
            )
        
        # Create journal header
        # Reference should be the expense ID (UUID as string)
        journal_data = JournalHeaderCreate(
            reference=str(expense_id),
            memo=f"{expense_type.title()} for {expense_number or expense_id}",
            posted_at=posted_at,
            extras={
                f"{expense_type}_id": str(expense_id),
                f"{expense_type}_number": expense_number,
                "reference_id": str(reference_id),
                "expense_type": expense_type
            },
            journal_lines=journal_lines
        )
        
        # Create journal with lines (without committing if commit=False)
        journal_header = self.create_journal_with_lines(
            data=journal_data,
            tenant_id=tenant_id,
            session=session,
            commit=commit
        )
        
        return journal_header

    def reverse_journal_for_expense(
        self,
        expense_id: uuid.UUID,
        expense_type: str,
        expense_number: Optional[str],
        reference_id: uuid.UUID,
        posted_at: datetime,
        tenant_id: uuid.UUID,
        existing_journal: JournalHeaderDB,
        session: Session,
        commit: bool = False
    ) -> JournalHeaderDB:
        """
        Reverse an existing journal entry by creating a reversal entry.
        The reversal swaps debits and credits to nullify the original entry.
        
        Args:
            expense_id: The ID of the expense transaction
            expense_type: Type of expense (bill, vendor_credit, etc.)
            expense_number: Optional reference number
            reference_id: ID of related entity (payee_id, vendor_id, etc.)
            posted_at: Date when the reversal is posted
            tenant_id: Tenant UUID
            existing_journal: The existing journal header to reverse
            session: Database session
            commit: Whether to commit the transaction (default False)
            
        Returns:
            JournalHeaderDB - The reversal journal header
        """
        # Convert tenant_id to UUID if it's a string
        if isinstance(tenant_id, str):
            tenant_id = uuid.UUID(tenant_id)
        
        # Get existing journal lines
        existing_lines_stmt = select(JournalLineDB).where(
            JournalLineDB.journal_header_id == existing_journal.id,
            JournalLineDB.tenant_id == tenant_id
        )
        existing_lines = session.exec(existing_lines_stmt).all()
        
        # Create reversal journal header
        reversal_memo = f"Reversal of {expense_type.title()} {expense_number or expense_id}"
        reversal_data = JournalHeaderCreate(
            reference=str(expense_id),
            memo=reversal_memo,
            posted_at=posted_at,
            extras={
                f"{expense_type}_id": str(expense_id),
                f"{expense_type}_number": expense_number,
                "reference_id": str(reference_id),
                "expense_type": expense_type,
                "is_reversal": True,
                "reversed_journal_id": str(existing_journal.id)
            },
            journal_lines=[]
        )
        
        # Create reversal lines (swap debits and credits)
        reversal_lines = []
        for old_line in existing_lines:
            reversal_lines.append(
                JournalLineCreate(
                    account_id=old_line.account_id,
                    debit=old_line.credit,  # Swap: old credit becomes new debit
                    credit=old_line.debit,  # Swap: old debit becomes new credit
                    extras={
                        **old_line.extras,
                        "is_reversal": True,
                        "reversed_line_id": str(old_line.id),
                        f"{expense_type}_id": str(expense_id)
                    },
                    journal_header_id=None
                )
            )
        
        reversal_data.journal_lines = reversal_lines
        
        # Create reversal journal entry
        reversal_journal = self.create_journal_with_lines(
            data=reversal_data,
            tenant_id=tenant_id,
            session=session,
            commit=commit
        )
        
        return reversal_journal

    def update_journal_for_expense(
        self,
        expense_id: uuid.UUID,
        expense_type: str,
        expense_number: Optional[str],
        reference_id: uuid.UUID,
        posted_at: datetime,
        tenant_id: uuid.UUID,
        journal_lines_data: List[JournalLineCreate],
        session: Session,
        commit: bool = True
    ) -> JournalHeaderDB:
        """
        Update journal entry for an expense by reversing the old journal and creating a new one.
        This is a generic method that can be used for all expense-related transactions.
        
        Args:
            expense_id: The ID of the expense transaction (bill_id, payment_id, etc.)
            expense_type: Type of expense (bill, vendor_credit, credit_card_credit, payment, etc.)
            expense_number: Optional reference number (bill_number, payment_number, etc.)
            reference_id: ID of related entity (payee_id, vendor_id, etc.)
            posted_at: Date when the transaction was posted
            tenant_id: Tenant UUID
            journal_lines_data: New journal lines from frontend
            session: Database session
            commit: Whether to commit the transaction (default True, set False for single transaction)
            
        Returns:
            JournalHeaderDB - The newly created journal header
        """
        # Convert tenant_id to UUID if it's a string
        if isinstance(tenant_id, str):
            tenant_id = uuid.UUID(tenant_id)
        
        # Find existing journal header by reference (expense_id)
        expense_id_str = str(expense_id)
        existing_journal_stmt = (
            select(JournalHeaderDB)
            .where(
                JournalHeaderDB.reference == expense_id_str,
                JournalHeaderDB.tenant_id == tenant_id
            )
            .order_by(JournalHeaderDB.created_at.desc())
        )
        existing_journals = session.exec(existing_journal_stmt).all()
        existing_journal = next(
            (journal for journal in existing_journals if not (journal.extras or {}).get("is_reversal")),
            None
        )
        
        # If old journal exists, reverse it
        if existing_journal:
            self.reverse_journal_for_expense(
                expense_id=expense_id,
                expense_type=expense_type,
                expense_number=expense_number,
                reference_id=reference_id,
                posted_at=posted_at,
                tenant_id=tenant_id,
                existing_journal=existing_journal,
                session=session,
                commit=False
            )
        
        # Create new journal entry with updated data
        new_journal = self.create_journal_for_expense(
            expense_id=expense_id,
            expense_type=expense_type,
            expense_number=expense_number,
            reference_id=reference_id,
            posted_at=posted_at,
            tenant_id=tenant_id,
            journal_lines_data=journal_lines_data,
            session=session,
            commit=commit
        )
        
        return new_journal


journal_service = JournalService()
