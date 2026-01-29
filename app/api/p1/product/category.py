import uuid
from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session

from app.db.connection.conn_rls import tenant_session_dependency
from app.models.rls.m_product_category_rls import (
    ProductCategoryRead, ProductCategoryCreate, ProductCategoryUpdate,
    ProductCategoryTree
)
from app.services.service_product_category import product_category_service

router = APIRouter()
TENANT_ID = "550e8400-e29b-41d4-a716-446655440000"

get_session = tenant_session_dependency(TENANT_ID)


@router.get("/category/", response_model=List[ProductCategoryTree], description="Get product categories as tree")
async def get_categories(
    session: Session = Depends(get_session)
):
    """Get all product categories in tree structure"""
    return product_category_service.get_category_tree(session, TENANT_ID)


@router.get("/category/{category_id}", response_model=ProductCategoryRead, description="Get a specific category")
async def get_category(
    category_id: uuid.UUID,
    session: Session = Depends(get_session)
):
    """Get a specific category by ID"""
    category = product_category_service.get_category_by_id(session, category_id)
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    return category


@router.post("/category/", response_model=ProductCategoryRead, description="Create a new product category")
async def create_category(
    data: ProductCategoryCreate,
    session: Session = Depends(get_session)
):
    """Create a new product category"""
    try:
        return product_category_service.create_category(session, data, TENANT_ID)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.patch("/category/{category_id}", response_model=ProductCategoryRead, description="Edit a product category or soft delete (set is_deleted=true)")
async def update_category(
    category_id: uuid.UUID,
    data: ProductCategoryUpdate,
    session: Session = Depends(get_session)
):
    """Edit a product category or soft delete by setting is_deleted=true"""
    try:
        updated = product_category_service.update_category(session, category_id, data, TENANT_ID)
        if not updated:
            raise HTTPException(status_code=404, detail="Category not found")
        return updated
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))



