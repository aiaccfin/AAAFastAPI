# app/schemas/schema_salestax.py
from pydantic import BaseModel, Field
from datetime import datetime

class TaxesCollected(BaseModel):
    GST: float = 0.0
    PST: float = 0.0
    HST: float = 0.0
    BST: float = 0.0
    GST1: float = 0.0
    PST1: float = 0.0
    HST1: float = 0.0
    BST1: float = 0.0
    GST2: float = 0.0
    PST2: float = 0.0
    HST2: float = 0.0
    BST2: float = 0.0

class Adjustments(BaseModel):
    adjustment1: float = 0.0
    adjustment2: float = 0.0
    rebate_adjustments: float = 0.0       # Box 107 (example)
    other_adjustments: float = 0.0        # Box 108
    bad_debt_adjustments: float = 0.0     # Box 104
    credit_notes: float = 0.0             # credit adjustments

class GST26Create(BaseModel):
    # Reporting period
    period_start: datetime = Field(..., description="Start of reporting period")
    period_end: datetime = Field(..., description="End of reporting period")
    
    # Tax jurisdiction
    province: str = Field(..., description="Province or territory")

    # Collected taxes
    taxes_collected: TaxesCollected
    
    # Adjustments
    adjustments: Adjustments = Field(default_factory=Adjustments)
    
    # Totals and calculations
    total_tax_collected: float = 0.0     # e.g. Box 105
    total_adjustments: float = 0.0
    net_tax_due: float = 0.0            # Box 109 (calculated: collected - adjustments)

    # Filing metadata
    filed_date: datetime | None = None
    reference_number: str | None = None
    
    
    notes: str | None = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)   
    created_by: str | None = None
    updated_by: str | None = None  
    is_submitted: bool = False
    is_amended: bool = False        
    is_deleted: bool = False
