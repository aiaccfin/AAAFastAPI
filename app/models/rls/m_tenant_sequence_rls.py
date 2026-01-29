import uuid
from sqlmodel import SQLModel, Field


class TenantSequenceDB(SQLModel, table=True):
    __tablename__ = "tenant_sequences"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    tenant_id: uuid.UUID = Field(primary_key=True)
    next_invoice_number: int = Field(default=1124)
    next_receipt_number: int = Field(default=80124)
    next_credit_number: int = Field(default=1110124)
    next_number_1: int = Field(default=100124)
    next_number_2: int = Field(default=200124)
    next_number_3: int = Field(default=300124)
    next_number_4: int = Field(default=400124)
    next_number_5: int = Field(default=500124)
    next_number_6: int = Field(default=600124)
    next_number_7: int = Field(default=700124)
    next_number_8: int = Field(default=800124)
    next_number_9: int = Field(default=900124)
