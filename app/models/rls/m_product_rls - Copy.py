# app/models/rls/m_product_rls.py
from sqlmodel import SQLModel, Field, UniqueConstraint, Relationship
from typing import Optional, Dict, Any, List, TYPE_CHECKING
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy import Column, ForeignKey
from enum import Enum
from datetime import datetime, date
import uuid

if TYPE_CHECKING:
    from app.models.rls.m_product_category_rls import ProductCategory


class ProductType(str, Enum):
    NON_INVENTORY = "Non-inventory"
    INVENTORY = "Inventory"
    SERVICE = "Service"
    COMBO = "Combo"


class ProductBase(SQLModel):
    name: str
    sku: Optional[str] = None
    type: ProductType
    is_active: bool = Field(default=True)
    
    # Category & Classification
    category_id: Optional[uuid.UUID] = None  # FK to product_categories_rls
    class_field: Optional[str] = Field(default=None)  # Placeholder field
    
    # Inventory Fields (only for Inventory type)
    quantity: Optional[float] = Field(default=0, ge=0)
    initial_quantity: Optional[float] = Field(default=0, ge=0)
    initial_quantity_date: Optional[date] = None
    inv_asset_acc: Optional[uuid.UUID] = None  # COA ID for inventory asset account
    
    # JSONB fields for flexible data
    sale_info: Dict[str, Any] = Field(default={}, sa_column=Column(JSONB))
    # Structure: {income_account: UUID, price: float, include_tax: bool, tax: UUID, description: str}
    
    purchase_info: Dict[str, Any] = Field(default={}, sa_column=Column(JSONB))
    # Structure: {expense_account: UUID, average_cost: float, include_tax: bool, tax: UUID, description: str}
    
    # Combo Information (only for Combo type)
    display_bundle: bool = Field(default=False)
    combo_list: List[Dict[str, Any]] = Field(default=[], sa_column=Column(JSONB))
    # Structure: [{id: UUID, qty: float}]


class Product(ProductBase, table=True):
    __tablename__ = "products_rls"
    __table_args__ = (
        UniqueConstraint("tenant_id", "sku", name="uix_tenant_sku"),
    )
    
    tenant_id: uuid.UUID = Field(index=True)  # RLS tenant field
    id: Optional[uuid.UUID] = Field(default_factory=uuid.uuid4, primary_key=True)
    
    # Foreign key to category (override from base class to add FK constraint)
    category_id: Optional[uuid.UUID] = Field(
        default=None,
        sa_column=Column(ForeignKey("product_categories_rls.id", ondelete="SET NULL"), nullable=True, index=True)
    )
    
    # Relationship to category
    category: Optional["ProductCategory"] = Relationship(back_populates="products")
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    created_by: Optional[str] = Field(default=None)
    updated_by: Optional[str] = Field(default=None)


# Request/Response Models
class ProductCreate(ProductBase):
    pass


class ProductUpdate(SQLModel):
    """Update model - type, quantity, initial_quantity, and initial_quantity_date are NOT allowed to edit"""
    name: Optional[str] = None
    sku: Optional[str] = None
    is_active: Optional[bool] = None
    category_id: Optional[uuid.UUID] = None
    class_field: Optional[str] = None
    # quantity, initial_quantity, and initial_quantity_date are NOT changeable via update
    # Use inventory adjustment endpoint to change quantity
    inv_asset_acc: Optional[uuid.UUID] = None
    sale_info: Optional[Dict[str, Any]] = None
    purchase_info: Optional[Dict[str, Any]] = None
    combo_list: Optional[List[Dict[str, Any]]] = None
    display_bundle: Optional[bool] = None


class ProductRead(ProductBase):
    id: uuid.UUID
    tenant_id: uuid.UUID
    created_at: datetime
    updated_at: datetime


class ProductReadList(SQLModel):
    """Simplified model for listing products"""
    id: uuid.UUID
    name: str
    sku: Optional[str]
    type: ProductType
    is_active: bool
    category_id: Optional[uuid.UUID]
    quantity: Optional[float]
    created_at: datetime
    updated_at: datetime


class ProductBulkImportItem(ProductBase):
    """Single item for bulk import"""
    pass


class ProductBulkImportRequest(SQLModel):
    """Bulk import request"""
    products: List[ProductBulkImportItem]


class ProductBulkImportResponse(SQLModel):
    """Bulk import response"""
    imported_count: int
    updated_count: int
    failed: List[Dict[str, Any]]  # [{name, sku, error}]


# Inventory Adjustment Models (for API only, no separate table)
class InventoryAdjustmentRequest(SQLModel):
    """Request model for inventory adjustment"""
    product_id: uuid.UUID
    change_in_qty: float  # Can be positive or negative
    new_qty_on_hand: float = Field(ge=0)
    old_qty_on_hand: float = Field(ge=0)  # Current quantity for validation
    inv_adjust_acc: uuid.UUID  # COA ID for inventory adjustment account
    adjustment_date: Optional[date] = None  # Optional, defaults to current date if not provided
    reason_for_adjust: Optional[str] = None


class InventoryAdjustmentResponse(SQLModel):
    """Response model for inventory adjustment"""
    product_id: uuid.UUID
    old_qty_on_hand: float
    new_qty_on_hand: float
    change_in_qty: float
    adjustment_date: date
    message: str

