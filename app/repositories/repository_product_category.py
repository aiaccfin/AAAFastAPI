# app/repositories/repository_product_category.py
from sqlmodel import Session, select
from app.models.rls.m_product_category_rls import ProductCategory, ProductCategoryCreate, ProductCategoryUpdate
from typing import List, Optional
from datetime import datetime
import uuid


class ProductCategoryRepository:
    def get_all(self, session: Session) -> List[ProductCategory]:
        statement = select(ProductCategory).where(ProductCategory.is_deleted == False)
        return session.exec(statement).all()
    
    def get_by_id(self, category_id: uuid.UUID, session: Session) -> Optional[ProductCategory]:
        return session.get(ProductCategory, category_id)
    
    def get_by_parent(
        self, 
        parent_id: Optional[uuid.UUID], 
        tenant_id: uuid.UUID, 
        session: Session
    ) -> List[ProductCategory]:
        statement = select(ProductCategory).where(
            (ProductCategory.parent_id == parent_id) &
            (ProductCategory.tenant_id == tenant_id) &
            (ProductCategory.is_deleted == False)
        )
        return session.exec(statement).all()
    
    def get_root_categories(self, tenant_id: uuid.UUID, session: Session) -> List[ProductCategory]:
        """Get all root categories (no parent)"""
        statement = select(ProductCategory).where(
            (ProductCategory.parent_id.is_(None)) &
            (ProductCategory.tenant_id == tenant_id) &
            (ProductCategory.is_deleted == False)
        )
        return session.exec(statement).all()
    
    def get_category_tree(self, tenant_id: uuid.UUID, session: Session) -> List[ProductCategory]:
        """Get all active categories for building tree"""
        statement = select(ProductCategory).where(
            (ProductCategory.tenant_id == tenant_id) &
            (ProductCategory.is_deleted == False) &
            (ProductCategory.is_active == True)
        )
        return session.exec(statement).all()
    
    def get_children(self, category_id: uuid.UUID, session: Session) -> List[ProductCategory]:
        """Get direct children of a category"""
        statement = select(ProductCategory).where(
            (ProductCategory.parent_id == category_id) &
            (ProductCategory.is_deleted == False)
        )
        return session.exec(statement).all()
    
    def get_all_descendants(self, category_id: uuid.UUID, session: Session) -> List[ProductCategory]:
        """Get all descendants recursively"""
        descendants = []
        children = self.get_children(category_id, session)
        for child in children:
            descendants.append(child)
            descendants.extend(self.get_all_descendants(child.id, session))
        return descendants
    
    def create_category(
        self, 
        category_data: ProductCategoryCreate, 
        tenant_id: uuid.UUID, 
        session: Session
    ) -> ProductCategory:
        db_category = ProductCategory(**category_data.dict(), tenant_id=tenant_id)
        session.add(db_category)
        session.commit()
        session.refresh(db_category)
        return db_category
    
    def save(self, category: ProductCategory, session: Session) -> ProductCategory:
        session.add(category)
        session.commit()
        session.refresh(category)
        return category
    
    def update_category(
        self,
        category_id: uuid.UUID,
        category_data: ProductCategoryUpdate,
        session: Session
    ) -> Optional[ProductCategory]:
        db_category = self.get_by_id(category_id, session)
        if not db_category:
            return None
        
        update_data = category_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            if hasattr(db_category, field):
                setattr(db_category, field, value)
        
        db_category.updated_at = datetime.utcnow()
        session.add(db_category)
        session.commit()
        session.refresh(db_category)
        return db_category
    
    def soft_delete_category(
        self,
        category_id: uuid.UUID,
        session: Session
    ) -> Optional[ProductCategory]:
        """Soft delete category and cascade to children"""
        db_category = self.get_by_id(category_id, session)
        if not db_category:
            return None
        
        # Soft delete this category
        db_category.is_deleted = True
        db_category.deleted_at = datetime.utcnow()
        db_category.updated_at = datetime.utcnow()
        
        # Soft delete all descendants
        descendants = self.get_all_descendants(category_id, session)
        for desc in descendants:
            desc.is_deleted = True
            desc.deleted_at = datetime.utcnow()
            desc.updated_at = datetime.utcnow()
            session.add(desc)
        
        session.add(db_category)
        session.commit()
        session.refresh(db_category)
        return db_category


product_category_repository = ProductCategoryRepository()

