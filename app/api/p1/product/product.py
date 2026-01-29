import uuid
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session

from app.db.connection.conn_rls import tenant_session_dependency
from app.models.rls.m_product_rls import (
    ProductRead, ProductCreate, ProductUpdate, ProductReadList,
    ProductType, ProductBulkImportRequest, ProductBulkImportResponse,
    InventoryAdjustmentRequest, InventoryAdjustmentResponse
)
from app.services.service_product import product_service

router = APIRouter()
TENANT_ID = "550e8400-e29b-41d4-a716-446655440000"

get_session = tenant_session_dependency(TENANT_ID)


@router.get("/", response_model=dict, description="List all products with pagination and filtering")
async def list_products(
    session: Session = Depends(get_session),
    search: Optional[str] = Query(None, description="Search by name or SKU"),
    type: Optional[List[ProductType]] = Query(None, description="Filter by product type"),
    category: Optional[List[uuid.UUID]] = Query(None, description="Filter by category IDs"),
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    sort_by: Optional[str] = Query(None, description="Sort field"),
    sort_order: Optional[str] = Query("asc", description="Sort order: asc or desc")
):
    """Get all products with pagination, filtering, and search"""
    products, total = product_service.list_products(
        session=session,
        tenant_id=TENANT_ID,
        search=search,
        types=type,
        category_ids=category,
        is_active=is_active,
        page=page,
        page_size=page_size,
        sort_by=sort_by,
        sort_order=sort_order
    )
    
    total_pages = (total + page_size - 1) // page_size
    
    return {
        "items": products,
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": total_pages
    }


@router.post("/", response_model=ProductRead, description="Create a new product")
async def create_product(
    data: ProductCreate,
    session: Session = Depends(get_session)
):
    """Create a new product"""
    try:
        return product_service.create_product(session, data, TENANT_ID)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/bulk-import/", response_model=ProductBulkImportResponse, description="Bulk import products from CSV")
async def bulk_import_products(
    data: ProductBulkImportRequest,
    session: Session = Depends(get_session)
):
    """Bulk import products from array"""
    try:
        return product_service.bulk_import_products(session, TENANT_ID, data)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{product_id}", response_model=ProductRead, description="Get a specific product by ID")
async def get_product(
    product_id: uuid.UUID,
    session: Session = Depends(get_session)
):
    """Get a specific product by ID"""
    product = product_service.get_product_by_id(session, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product


@router.put("/{product_id}", response_model=ProductRead, description="Update an existing product (full update)")
async def update_product(
    product_id: uuid.UUID,
    data: ProductUpdate,
    session: Session = Depends(get_session)
):
    """Update an existing product. Type field is not allowed to edit."""
    try:
        updated = product_service.update_product(session, product_id, data)
        if not updated:
            raise HTTPException(status_code=404, detail="Product not found")
        return updated
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.patch("/{product_id}", response_model=ProductRead, description="Activate/deactivate a product")
async def activate_deactivate_product(
    product_id: uuid.UUID,
    is_active: bool = Query(..., description="Active status"),
    session: Session = Depends(get_session)
):
    """Activate or deactivate a product"""
    product = product_service.activate_deactivate_product(session, product_id, is_active)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product


@router.post("/inv_adjust/", response_model=InventoryAdjustmentResponse, description="Create a new inventory adjustment")
async def create_inventory_adjustment(
    data: InventoryAdjustmentRequest,
    session: Session = Depends(get_session)
):
    """
    Create a new inventory adjustment.
    Updates product quantity and validates quantity consistency.
    Change is automatically logged in audit_logs via database trigger.
    """
    try:
        return product_service.adjust_inventory(session, TENANT_ID, data)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

