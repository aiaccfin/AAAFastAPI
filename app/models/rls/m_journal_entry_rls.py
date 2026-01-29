from sqlmodel import SQLModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy import Column, Integer, Sequence
import uuid

# Define the Journal Entry Base model
class JournalEntryBase(SQLModel):
    description: Optional[str] = Field(default=None)  # Optional description for the journal entry
    transaction_date: Optional[datetime] = Field(default_factory=datetime.utcnow)
    account_id: str  # Account associated with the journal entry (e.g., Account Payable, Revenue)
    
    # Amount-related fields
    debit_amount: float = Field(ge=0, default=0)  # Debit amount
    credit_amount: float = Field(ge=0, default=0)  # Credit amount
    balance: float = Field(ge=0)  # Running balance for the journal entry
    
    # Optional fields
    reference_invoice_id: Optional[uuid.UUID] = Field(default=None)  # Linked invoice ID if applicable
    notes: Optional[Dict[str, Any]] = Field(default={}, sa_column=Column(JSONB))  # Additional notes or custom fields
    
    # Transaction status
    status: str = Field(default="draft")  # journal status: draft, finalized, etc.

# Define the actual JournalEntry model for the table
class JournalEntry(JournalEntryBase, table=True):
    __tablename__ = "journal_entries"
    
    # Primary key and auto-generated UUID
    id: Optional[uuid.UUID] = Field(default_factory=uuid.uuid4, primary_key=True)
    
    # Foreign key relationship (could be linked to a specific tenant or company)
    tenant_id: str = Field(index=True)  # Tenant-dependent field
    
    journal_lines: List[Dict[str, Any]] = Field(
        default=[], sa_column=Column(JSONB)
    )
    
    # Sequence for journal entry number (using SQLAlchemy's Sequence in Column definition)
    journal_entry_prefix: str = Field(default="JE-", index=True)  # Prefix for journal entry number
    journal_entry_sequence: int = Field(sa_column=Column(Integer, Sequence('journal_entry_seq', start=1001, increment=1), nullable=False))
    
    # Automatically generated journal entry number
    @property
    def full_journal_entry_number(self) -> str:
        return f"{self.journal_entry_prefix}-{self.journal_entry_sequence:04d}"  # JE-0001
    
    # Automatic metadata fields
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    created_by: Optional[str] = Field(default=None)

    class Config:
        # You can define indexes here if needed
        indexes = [
            ("tenant_id", "journal_entry_number"),
            ("tenant_id", "status"),
            ("tenant_id", "transaction_date"),
        ]


# Model for creating new Journal Entries
class JournalEntryCreate(JournalEntryBase):
    pass

# Model for reading Journal Entries (with additional metadata)
class JournalEntryRead(JournalEntryBase):
    id: uuid.UUID  # The actual UUID of the journal entry
    tenant_id: str
    journal_entry_prefix: str
    journal_entry_sequence: int
    full_journal_entry_number: str  # Full journal entry number
    created_at: datetime
    updated_at: datetime
