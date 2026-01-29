# app/services/service_product_category.py
from typing import List, Optional
import uuid
from sqlmodel import Session
from fastapi import HTTPException
from app.models.rls.m_product_category_rls import (
    ProductCategory, ProductCategoryCreate, ProductCategoryUpdate,
    ProductCategoryRead, ProductCategoryTree
)
from app.repositories.repository_product_category import product_category_repository
from app.repositories.repository_product import product_repository


class ProductCategoryService:
    
    def get_category_tree(self, session: Session, tenant_id: str) -> List[ProductCategoryTree]:
        """Get category tree structure"""
        tenant_uuid = uuid.UUID(tenant_id) if isinstance(tenant_id, str) else tenant_id
        all_categories = product_category_repository.get_category_tree(tenant_uuid, session)
        
        # Build tree structure
        category_map = {cat.id: ProductCategoryTree(**cat.dict(), children=[]) for cat in all_categories}
        root_categories = []
        
        for category in all_categories:
            tree_node = category_map[category.id]
            if category.parent_id is None:
                root_categories.append(tree_node)
            else:
                parent = category_map.get(category.parent_id)
                if parent:
                    parent.children.append(tree_node)
        
        return root_categories
    
    def get_category_by_id(self, session: Session, category_id: uuid.UUID) -> Optional[ProductCategoryRead]:
        category = product_category_repository.get_by_id(category_id, session)
        if not category:
            return None
        return ProductCategoryRead(**category.dict())
    
    def create_category(
        self,
        session: Session,
        category_data: ProductCategoryCreate,
        tenant_id: str
    ) -> ProductCategoryRead:
        # Convert tenant_id to UUID for comparison
        tenant_uuid = uuid.UUID(tenant_id) if isinstance(tenant_id, str) else tenant_id
        
        # Validate parent exists if provided
        if category_data.parent_id:
            parent = product_category_repository.get_by_id(category_data.parent_id, session)
            if not parent:
                raise HTTPException(status_code=404, detail="Parent category not found")
            
            # Compare tenant_id (convert both to UUID)
            parent_tenant_uuid = parent.tenant_id if isinstance(parent.tenant_id, uuid.UUID) else uuid.UUID(str(parent.tenant_id))
            if parent_tenant_uuid != tenant_uuid:
                raise HTTPException(status_code=404, detail="Parent category not found")
            
            if parent.is_deleted:
                raise HTTPException(status_code=400, detail="Cannot create category under deleted parent")
        
        # Build path if parent exists
        if category_data.parent_id:
            parent = product_category_repository.get_by_id(category_data.parent_id, session)
            if parent and parent.path:
                category_data.path = f"{parent.path}/{category_data.name}"
            else:
                category_data.path = f"/{category_data.name}"
        else:
            category_data.path = f"/{category_data.name}"
        
        category = product_category_repository.create_category(category_data, tenant_uuid, session)
        return ProductCategoryRead(**category.dict())
    
    def update_category(
        self,
        session: Session,
        category_id: uuid.UUID,
        category_data: ProductCategoryUpdate,
        tenant_id: Optional[str] = None
    ) -> Optional[ProductCategoryRead]:
        category = product_category_repository.get_by_id(category_id, session)
        if not category:
            return None
        
        # Handle soft delete if is_deleted is set to True
        update_dict = category_data.dict(exclude_unset=True)
        if update_dict.get('is_deleted') is True:
            tenant_uuid = uuid.UUID(tenant_id) if tenant_id and isinstance(tenant_id, str) else (tenant_id or category.tenant_id)
            success = self.delete_category(session, category_id, str(tenant_uuid))
            if success:
                deleted_category = self.get_category_by_id(session, category_id)
                return deleted_category
            return None
        
        # Validate parent if changing
        if category_data.parent_id is not None and category_data.parent_id != category.parent_id:
            if category_data.parent_id == category_id:
                raise HTTPException(status_code=400, detail="Category cannot be its own parent")
            
            parent = product_category_repository.get_by_id(category_data.parent_id, session)
            if not parent:
                raise HTTPException(status_code=404, detail="Parent category not found")
            
            # Check for circular reference
            descendants = product_category_repository.get_all_descendants(category_id, session)
            if any(desc.id == category_data.parent_id for desc in descendants):
                raise HTTPException(status_code=400, detail="Cannot set parent to a descendant category")
        
        updated = product_category_repository.update_category(category_id, category_data, session)
        if not updated:
            return None
        
        return ProductCategoryRead(**updated.dict())
    
    def delete_category(
        self,
        session: Session,
        category_id: uuid.UUID,
        tenant_id: str
    ) -> bool:
        tenant_uuid = uuid.UUID(tenant_id) if isinstance(tenant_id, str) else tenant_id
        category = product_category_repository.get_by_id(category_id, session)
        if not category:
            return False
        
        # Compare tenant_id (convert both to UUID)
        category_tenant_uuid = category.tenant_id if isinstance(category.tenant_id, uuid.UUID) else uuid.UUID(str(category.tenant_id))
        if category_tenant_uuid != tenant_uuid:
            return False
        
        # Decategorize all products in this category and its descendants
        descendants = product_category_repository.get_all_descendants(category_id, session)
        all_category_ids = [category_id] + [desc.id for desc in descendants]
        
        for cat_id in all_category_ids:
            products = product_repository.get_by_category(cat_id, tenant_id, session)
            for product in products:
                product.category_id = None
                product_repository.save(product, session)
        
        # Soft delete category and descendants
        product_category_repository.soft_delete_category(category_id, session)
        return True


product_category_service = ProductCategoryService()

