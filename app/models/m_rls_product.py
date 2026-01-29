# app/models/product.py
from sqlmodel import SQLModel, Field
from typing import Optional, Dict, Any
from datetime import datetime
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy import Column


class ProductBase(SQLModel):
    # 核心业务字段（结构化）
    product_code: str = Field(index=True)
    product_name: str
    unit_price: float = Field(ge=0)
    is_active: bool = Field(default=True)

    # JSONB 灵活数据
    product_data: Dict[str, Any] = Field(default={}, sa_column=Column(JSONB))
    pricing_data: Dict[str, Any] = Field(default={}, sa_column=Column(JSONB))
    openai_data: Dict[str, Any] = Field(default={}, sa_column=Column(JSONB))


class Product(ProductBase, table=True):
    __tablename__ = "products"
    id: Optional[int] = Field(default=None, primary_key=True)
    tenant_id: str = Field(index=True)  # 🔥 RLS 依赖这个字段

    # 自动元数据
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    created_by: Optional[str] = Field(default=None)


class ProductCreate(ProductBase):
    """创建产品时的输入模型"""

    pass


class ProductRead(ProductBase):
    """读取产品时的输出模型"""

    id: int
    tenant_id: str
    created_at: datetime
    updated_at: datetime
