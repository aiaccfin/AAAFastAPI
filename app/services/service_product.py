# app/services/service_product.py
from typing import List, Optional, Dict, Any
import uuid
from datetime import date
from sqlmodel import Session
from fastapi import HTTPException
from app.models.rls.m_product_rls import (
    Product, ProductCreate, ProductUpdate, ProductRead, ProductReadList,
    ProductType, ProductBulkImportRequest, ProductBulkImportResponse,
    InventoryAdjustmentRequest, InventoryAdjustmentResponse
)
from app.repositories.repository_product import product_repository


class ProductService:
    
    def list_products(
        self,
        session: Session,
        tenant_id: uuid.UUID,
        search: Optional[str] = None,
        types: Optional[List[ProductType]] = None,
        category_ids: Optional[List[uuid.UUID]] = None,
        is_active: Optional[bool] = None,
        page: int = 1,
        page_size: int = 20,
        sort_by: Optional[str] = None,
        sort_order: Optional[str] = "asc"
    ) -> tuple[List[ProductReadList], int]:
        skip = (page - 1) * page_size
        
        products, total = product_repository.search_products(
            tenant_id=tenant_id,
            session=session,
            search=search,
            types=types,
            category_ids=category_ids,
            is_active=is_active,
            skip=skip,
            limit=page_size
        )
        
        # Convert to read list
        product_list = [ProductReadList(**product.dict()) for product in products]
        return product_list, total
    
    def get_product_by_id(self, session: Session, product_id: uuid.UUID) -> Optional[ProductRead]:
        product = product_repository.get_by_id(product_id, session)
        if not product:
            return None
        return ProductRead(**product.dict())
    
    def create_product(
        self,
        session: Session,
        product_data: ProductCreate,
        tenant_id: uuid.UUID
    ) -> ProductRead:
        """Create a product"""
        # Validate type-specific requirements
        self._validate_product_create(product_data)
        
        # Check SKU uniqueness if provided
        if product_data.sku:
            existing = product_repository.get_by_sku(product_data.sku, tenant_id, session)
            if existing:
                raise HTTPException(status_code=400, detail=f"Product with SKU '{product_data.sku}' already exists")
        
        # Create product
        db_product = Product(**product_data.dict(), tenant_id=tenant_id)
        session.add(db_product)
        session.commit()
        session.refresh(db_product)
        
        return ProductRead(**db_product.dict())
    
    def update_product(
        self,
        session: Session,
        product_id: uuid.UUID,
        product_data: ProductUpdate
    ) -> Optional[ProductRead]:
        product = product_repository.get_by_id(product_id, session)
        if not product:
            return None
        
        # Validate update data
        self._validate_product_update(product, product_data)
        
        updated = product_repository.update_product(product_id, product_data, session)
        if not updated:
            return None
        
        return ProductRead(**updated.dict())
    
    def activate_deactivate_product(
        self,
        session: Session,
        product_id: uuid.UUID,
        is_active: bool
    ) -> Optional[ProductRead]:
        product = product_repository.update_active_status(product_id, is_active, session)
        if not product:
            return None
        return ProductRead(**product.dict())
    
    def bulk_import_products(
        self,
        session: Session,
        tenant_id: uuid.UUID,
        bulk_data: ProductBulkImportRequest
    ) -> ProductBulkImportResponse:
        imported_count = 0
        updated_count = 0
        failed = []
        
        for product_item in bulk_data.products:
            try:
                # Validate
                self._validate_product_create(product_item)
                
                # Check if exists by SKU
                if product_item.sku:
                    existing = product_repository.get_by_sku(product_item.sku, tenant_id, session)
                    if existing:
                        # Update existing
                        update_data = ProductUpdate(**product_item.dict())
                        product_repository.update_product(existing.id, update_data, session)
                        session.commit()  # Commit update
                        updated_count += 1
                    else:
                        # Create new
                        db_product = Product(**product_item.dict(), tenant_id=tenant_id)
                        session.add(db_product)
                        session.commit()
                        session.refresh(db_product)
                        imported_count += 1
                else:
                    # Create new without SKU
                    db_product = Product(**product_item.dict(), tenant_id=tenant_id)
                    session.add(db_product)
                    session.commit()
                    session.refresh(db_product)
                    imported_count += 1
            except Exception as e:
                # If this product fails, rollback this product's changes
                # Previous successfully committed products remain saved
                session.rollback()
                failed.append({
                    "name": product_item.name,
                    "sku": product_item.sku or "",
                    "error": str(e)
                })
                # Continue processing remaining products
        
        return ProductBulkImportResponse(
            imported_count=imported_count,
            updated_count=updated_count,
            failed=failed
        )
    
    def _validate_product_create(self, product_data: ProductCreate):
        """Validate product creation data"""
        if product_data.type == ProductType.INVENTORY:
            if product_data.inv_asset_acc is None:
                raise HTTPException(
                    status_code=400,
                    detail="inv_asset_acc is required for Inventory type products"
                )
            if product_data.quantity is None:
                product_data.quantity = 0
            if product_data.initial_quantity is None:
                product_data.initial_quantity = 0
        
        if product_data.type == ProductType.COMBO:
            if not product_data.combo_list:
                raise HTTPException(
                    status_code=400,
                    detail="combo_list is required for Combo type products"
                )
    
    def _validate_product_update(self, product: Product, update_data: ProductUpdate):
        """Validate product update data"""
        # Type cannot be changed (type field is not in ProductUpdate, so this check is not needed)
        # But we validate based on the existing product type
        
        # Explicitly prevent updating quantity, initial_quantity, and initial_quantity_date
        # These fields should only be set during creation or via inventory adjustment
        update_dict = update_data.dict(exclude_unset=True)
        if 'quantity' in update_dict:
            raise HTTPException(
                status_code=400,
                detail="quantity cannot be changed via update. Use inventory adjustment endpoint to change quantity."
            )
        if 'initial_quantity' in update_dict:
            raise HTTPException(
                status_code=400,
                detail="initial_quantity cannot be changed after product creation."
            )
        if 'initial_quantity_date' in update_dict:
            raise HTTPException(
                status_code=400,
                detail="initial_quantity_date cannot be changed after product creation."
            )
        
        # Validate type-specific fields
        if product.type == ProductType.INVENTORY:
            # If trying to set inv_asset_acc to None, prevent it
            if hasattr(update_data, 'inv_asset_acc') and update_data.inv_asset_acc is None:
                raise HTTPException(
                    status_code=400,
                    detail="inv_asset_acc cannot be removed for Inventory type products"
                )
    
    def adjust_inventory(
        self,
        session: Session,
        tenant_id: str,
        adjustment_data: InventoryAdjustmentRequest
    ) -> Dict[str, Any]:
        """
        Adjust inventory quantity for a product.
        Validates quantities and updates product.quantity.
        Audit logging is handled by database trigger.
        """
        # Convert tenant_id to UUID for comparison
        tenant_uuid = uuid.UUID(tenant_id) if isinstance(tenant_id, str) else tenant_id
        
        # Use system date if adjustment_date is not provided
        adjustment_date = adjustment_data.adjustment_date or date.today()
        
        # Get product (RLS already filters by tenant via session)
        product = product_repository.get_by_id(adjustment_data.product_id, session)
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")
        
        # Validate tenant (convert product.tenant_id to UUID if needed)
        product_tenant_uuid = product.tenant_id if isinstance(product.tenant_id, uuid.UUID) else uuid.UUID(str(product.tenant_id))
        if product_tenant_uuid != tenant_uuid:
            raise HTTPException(status_code=403, detail="Product belongs to different tenant")
        
        # Validate product type
        if product.type != ProductType.INVENTORY:
            raise HTTPException(
                status_code=400,
                detail="Inventory adjustments can only be made for Inventory type products"
            )
        
        # Validate old_qty_on_hand matches current quantity (prevents race conditions)
        if abs(product.quantity - adjustment_data.old_qty_on_hand) > 0.01:
            raise HTTPException(
                status_code=400,
                detail=f"Current product quantity ({product.quantity}) does not match "
                       f"old_qty_on_hand ({adjustment_data.old_qty_on_hand}). "
                       f"Please refresh and try again."
            )
        
        # Validate quantity consistency
        expected_new_qty = adjustment_data.old_qty_on_hand + adjustment_data.change_in_qty
        if abs(expected_new_qty - adjustment_data.new_qty_on_hand) > 0.01:
            raise HTTPException(
                status_code=400,
                detail=f"Quantity mismatch: new_qty_on_hand ({adjustment_data.new_qty_on_hand}) "
                       f"should equal old_qty_on_hand ({adjustment_data.old_qty_on_hand}) + "
                       f"change_in_qty ({adjustment_data.change_in_qty})"
            )
        
        # Update product quantity
        update_data = ProductUpdate(quantity=adjustment_data.new_qty_on_hand)
        updated_product = product_repository.update_product(adjustment_data.product_id, update_data, session)
        
        if not updated_product:
            raise HTTPException(status_code=500, detail="Failed to update product quantity")
        
        # Return response
        return {
            "product_id": adjustment_data.product_id,
            "old_qty_on_hand": adjustment_data.old_qty_on_hand,
            "new_qty_on_hand": adjustment_data.new_qty_on_hand,
            "change_in_qty": adjustment_data.change_in_qty,
            "adjustment_date": adjustment_date,  # Use resolved date (system date if not provided)
            "message": "Inventory adjusted successfully. Change logged in audit_logs."
        }
    

product_service = ProductService()

