# app/models/rls/m_product_category_rls.py
from sqlmodel import SQLModel, Field, UniqueConstraint, Relationship
from typing import Optional, List, TYPE_CHECKING
from sqlalchemy import Column, ForeignKey
from pydantic import field_validator
from datetime import datetime
import uuid

if TYPE_CHECKING:
    from app.models.rls.m_product_rls import Product


class ProductCategoryBase(SQLModel):
    name: str
    parent_id: Optional[uuid.UUID] = None  # Self-referencing FK for hierarchical structure
    path: Optional[str] = None  # Materialized path: "/Electronics/Computers/Laptops"
    is_active: bool = Field(default=True)
    is_deleted: bool = Field(default=False)


class ProductCategory(ProductCategoryBase, table=True):
    __tablename__ = "product_categories_rls"
    __table_args__ = (
        UniqueConstraint("tenant_id", "name", "parent_id", name="uix_tenant_name_parent"),
    )
    
    tenant_id: uuid.UUID = Field(index=True)  # RLS tenant field
    id: Optional[uuid.UUID] = Field(default_factory=uuid.uuid4, primary_key=True)
    
    # Self-referencing foreign key for hierarchical structure (override from base class)
    parent_id: Optional[uuid.UUID] = Field(
        default=None,
        sa_column=Column(ForeignKey("product_categories_rls.id", ondelete="SET NULL"), nullable=True, index=True)
    )
    
    # Relationships
    parent: Optional["ProductCategory"] = Relationship(
        back_populates="children",
        sa_relationship_kwargs={
            "remote_side": "ProductCategory.id"
        }
    )
    children: List["ProductCategory"] = Relationship(back_populates="parent")
    
    # Relationship to products
    products: List["Product"] = Relationship(back_populates="category")
    
    deleted_at: Optional[datetime] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    created_by: Optional[str] = Field(default=None)
    updated_by: Optional[str] = Field(default=None)


# Request/Response Models
class ProductCategoryCreate(ProductCategoryBase):
    @field_validator('parent_id', mode='before')
    @classmethod
    def convert_empty_string_to_none(cls, v):
        """Convert empty string to None for parent_id"""
        if v == "" or v is None:
            return None
        return v


class ProductCategoryUpdate(SQLModel):
    name: Optional[str] = None
    parent_id: Optional[uuid.UUID] = None
    path: Optional[str] = None
    is_active: Optional[bool] = None
    is_deleted: Optional[bool] = None  # Set to True to soft delete
    
    @field_validator('parent_id', mode='before')
    @classmethod
    def convert_empty_string_to_none(cls, v):
        """Convert empty string to None for parent_id"""
        if v == "" or v is None:
            return None
        return v


class ProductCategoryRead(ProductCategoryBase):
    id: uuid.UUID
    tenant_id: uuid.UUID
    created_at: datetime
    updated_at: datetime
    deleted_at: Optional[datetime]


class ProductCategoryTree(ProductCategoryRead):
    """Category with children for tree structure"""
    children: List["ProductCategoryTree"] = Field(default_factory=list)

