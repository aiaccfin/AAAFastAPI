from pydantic import BaseModel, EmailStr, Field
from typing import Any, Optional, Dict
from datetime import datetime


class Address(BaseModel):
    """Nested model for client address."""
    street: str
    city: str
    state: str
    zip: str
    country: Optional[str] = None  # Optional field to store country


class ClientBase(BaseModel):
    """Base model with optional fields for flexibility."""
    client_id: Optional[str] = "C001"
    client_number: Optional[str] = "CL-1001"
    client_business_number: Optional[str] = "868-588-001"
    client_company_name: Optional[str] = "White House Inc."
    client_contact_name: Optional[str] = "Donald Trump"
    client_contact_title: Optional[str] = "CEO"
    client_email: Optional[EmailStr] = "trump@whitehouse.com"
    client_mainphone: Optional[str] = "+1-202-456-1111"
    client_secondphone: Optional[str] = "+1-202-456-2222"
    client_fax: Optional[str] = "+1-202-456-7890"
    client_website: Optional[str] = "https://whitehouse.gov"
    client_currency: Optional[str] = "USD"
    client_tax_id: Optional[str] = "123456789"
    client_payment_term: Optional[int] = 30
    client_payment_method: Optional[str] = "Bank Transfer"
    client_template_id: Optional[str] = "template-001"
    client_terms_conditions: Optional[str] = "Payment due within 30 days."
    client_note: Optional[str] = "Preferred client"
    client_address: Optional[Address] = None  # Nested Address
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Fields that can be added dynamically
    extra_fields: Optional[Dict[str, Any]] = {}

    class Config:
        from_attributes = True  # To handle MongoDB conversion
        extra = "allow"
        

class ClientCreate(ClientBase):
    """For creating new clients."""
    pass


class ClientUpdate(ClientBase):
    """For updating existing clients with flexible fields."""
    pass


class ClientResponse(ClientBase):
    """Response model for a client."""
    id: str
    created_at: datetime

    class Config:
        from_attributes = True
