from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import datetime


class Attributes(BaseModel):
    color: str = "Silver"
    weight_kg: float = 1.5
    warranty_years: int = 2


# ---- InvoiceItem Extended ----
class InvoiceItem(BaseModel):
    # ✅ original fields
    item_id: str = "ITEM001"
    item_number: str = "1001"
    item_name: str = "Consulting Service"
    item_description: str = "One hour consulting session"
    item_sku: str = "SKU-001"
    item_rate: float = 100.0
    item_tax_code_id: str = "TAX001"
    item_tax_rate: float = 0.07
    item_tax_amount: float = 7.0
    item_currency: str = "USD"
    item_unit: str = "hour"
    item_note: str = "Billed per hour"
    item_quantity: int = 1
    item_amount: float = 107.0
    item_reorder_level: int = 2

    # ✅ extra fields with realistic defaults
    item_category: str = "Electronics"
    item_brand: str = "BrandName"
    item_attributes: Attributes = Attributes()

    status: str = "Draft"
    is_active: int = 1
    is_locked: int = 0
    is_deleted: int = 0
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        extra = "allow"  # allow user to add new fields dynamically


class InvoiceCustomer(BaseModel):
    customer_id: str = "C001"
    customer_number: str = "CL-1001"
    customer_business_number: str = "868-588-001"
    customer_company_name: str = "White House Inc."
    customer_contact_name: str = "Donald Trump"
    customer_contact_title: str = "CEO"
    customer_address1: str = "1601 Pennsylvania Ave NW, Washington, DC 20500"
    customer_address2: str = "1602 Pennsylvania Ave NW, Washington, DC 20500"
    customer_address3: str = "1603 Pennsylvania Ave NW, Washington, DC 20500"
    customer_email: str = "trump@whitehouse.com"
    customer_mainphone: str = "+1-202-456-1111"
    customer_secondphone: str = "+1-202-456-2222"
    customer_fax: str = "+1-202-456-7890"
    customer_website: str = "https://whitehouse.gov"
    customer_currency: str = "USD"
    customer_tax_id: str = "123456789"
    customer_payment_term: int = 30
    customer_payment_method: str = "Bank Transfer"
    customer_template_id: str = "template-001"
    customer_terms_conditions: str = "Payment due within 30 days."
    customer_note: str = "Preferred customer"


class InvoiceModel(BaseModel):
    # Required
    inv_id: str
    inv_number: int = 1000

    # Optional with realistic defaults
    user_id: int = 1
    be_id: int = 1

    customer_id: str = "C001"
    customer: InvoiceCustomer = InvoiceCustomer()

    inv_date: datetime = datetime.utcnow()
    inv_due_date: datetime = datetime.utcnow()

    inv_title: str = "Standard Invoice"
    inv_payment_requirement: str = "Net 30 days"
    inv_payment_term: int = 30
    inv_reference: str = "PO-001"
    inv_currency: str = "USD"

    inv_subtotal: float = 100.0
    inv_discount_type: str = "Percentage"
    inv_discount_rate: float = 0.0
    inv_discount_value: float = 0.0
    inv_discount_amount: float = 0.0

    inv_tax_label: str = "Tax"
    inv_tax_rate: float = 0.07
    inv_tax_amount: float = 7.0
    inv_shipping: float = 0.0
    inv_handling: float = 0.0
    inv_deposit: float = 0.0
    inv_adjustment: float = 0.0
    inv_other_charges_label: str = "Other Charges"
    inv_other_charges_amount: float = 0.0
    inv_total: float = 107.0

    inv_paid_total: float = 0.0
    inv_balance_due: float = 107.0
    inv_payment_status: str = "Unpaid"

    inv_flag_word: str = "Unpaid"
    inv_flag_emoji: str = "🟡"

    inv_pdf_template: str = "default"
    inv_notes: str = "Thank you for your business!"
    inv_terms_conditions: str = "Payment due in 30 days."

    inv_items: List[InvoiceItem] = [InvoiceItem()]
    inv_payments: List[Dict[str, Any]] = []

    status: str = "Draft"
    is_active: int = 1
    is_locked: int = 0
    is_deleted: int = 0
    is_void: int = 0

    mark_as_sent: int = 0
    auto_apply: int = 0

    # created_at: datetime = datetime.utcnow()
    # updated_at: datetime = datetime.utcnow()
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        extra = "allow"  # allow user to add new fields dynamically
