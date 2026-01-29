from typing import Optional
from datetime import datetime
from sqlmodel import SQLModel, Field


class TaxBase(SQLModel):
    user_id: Optional[int] = Field(default=1, description="The owner (freelancer/micro biz user)")
    biz_id: Optional[str] = Field(default="666", description="Business identifier")

    tax_name: Optional[str] = Field(default="HST", description="Name of the tax")
    tax_rate: Optional[float] = Field(default=0.13, description="Rate of the tax")
    tax_number: Optional[str] = Field(default="123456789RT0001", description="Tax registration number")
    tax_type: Optional[str] = Field(default="type", description="Type/category of the tax")
    tax_note: Optional[str] = Field(default="Tax note.", description="Note or comment about the tax")
    tax_status: Optional[str] = Field(default="active", description="Status of the tax")

    is_locked: Optional[int] = Field(default=0)
    is_deleted: Optional[int] = Field(default=0)

    created_at: Optional[str] = Field(default_factory=lambda: datetime.utcnow().isoformat())
    updated_at: Optional[str] = Field(default_factory=lambda: datetime.utcnow().isoformat())


class Tax(TaxBase, table=True):
    __tablename__ = "tax"
    id: Optional[int] = Field(default=None, primary_key=True)


class TaxCreate(TaxBase):
    pass


class TaxUpdate(TaxBase):
    pass


class TaxRead(TaxBase):
    id: int
