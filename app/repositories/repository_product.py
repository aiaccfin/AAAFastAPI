# app/repositories/repository_product.py
from sqlmodel import Session, select, func, or_
from app.models.rls.m_product_rls import Product, ProductCreate, ProductUpdate, ProductType
from typing import List, Optional
from datetime import datetime
import uuid


class ProductRepository:
    def get_all(self, session: Session) -> List[Product]:
        statement = select(Product)
        return session.exec(statement).all()
    
    def get_by_id(self, product_id: uuid.UUID, session: Session) -> Optional[Product]:
        return session.get(Product, product_id)
    
    def get_by_sku(self, sku: str, tenant_id: uuid.UUID, session: Session) -> Optional[Product]:
        statement = select(Product).where(
            (Product.sku == sku) & 
            (Product.tenant_id == tenant_id)
        )
        return session.exec(statement).first()
    
    def get_by_type(self, product_type: ProductType, tenant_id: uuid.UUID, session: Session) -> List[Product]:
        statement = select(Product).where(
            (Product.type == product_type) & 
            (Product.tenant_id == tenant_id)
        )
        return session.exec(statement).all()
    
    def get_by_category(self, category_id: uuid.UUID, tenant_id: uuid.UUID, session: Session) -> List[Product]:
        statement = select(Product).where(
            (Product.category_id == category_id) & 
            (Product.tenant_id == tenant_id)
        )
        return session.exec(statement).all()
    
    def search_products(
        self, 
        tenant_id: uuid.UUID,
        session: Session,
        search: Optional[str] = None,
        types: Optional[List[ProductType]] = None,
        category_ids: Optional[List[uuid.UUID]] = None,
        is_active: Optional[bool] = None,
        skip: int = 0,
        limit: int = 100
    ) -> tuple[List[Product], int]:
        statement = select(Product).where(Product.tenant_id == tenant_id)
        count_statement = select(func.count()).select_from(Product).where(Product.tenant_id == tenant_id)
        
        if search:
            search_filter = or_(
                Product.name.ilike(f"%{search}%"),
                Product.sku.ilike(f"%{search}%")
            )
            statement = statement.where(search_filter)
            count_statement = count_statement.where(search_filter)
        
        if types:
            statement = statement.where(Product.type.in_(types))
            count_statement = count_statement.where(Product.type.in_(types))
        
        if category_ids:
            statement = statement.where(Product.category_id.in_(category_ids))
            count_statement = count_statement.where(Product.category_id.in_(category_ids))
        
        if is_active is not None:
            statement = statement.where(Product.is_active == is_active)
            count_statement = count_statement.where(Product.is_active == is_active)
        
        total = session.exec(count_statement).one()
        products = session.exec(statement.offset(skip).limit(limit)).all()
        
        return products, total
    
    def create_product(self, product_data: ProductCreate, tenant_id: uuid.UUID, session: Session) -> Product:
        db_product = Product(**product_data.dict(), tenant_id=tenant_id)
        session.add(db_product)
        session.commit()
        session.refresh(db_product)
        return db_product
    
    def save(self, product: Product, session: Session) -> Product:
        session.add(product)
        session.commit()
        session.refresh(product)
        return product
    
    def update_product(
        self, 
        product_id: uuid.UUID, 
        product_data: ProductUpdate, 
        session: Session
    ) -> Optional[Product]:
        db_product = self.get_by_id(product_id, session)
        if not db_product:
            return None
        
        update_data = product_data.dict(exclude_unset=True)
        
        # Explicitly exclude quantity, initial_quantity, and initial_quantity_date from updates
        # These fields should only be set during creation or via inventory adjustment
        excluded_fields = {'quantity', 'initial_quantity', 'initial_quantity_date', 'type'}
        update_data = {k: v for k, v in update_data.items() if k not in excluded_fields}
        
        for field, value in update_data.items():
            if hasattr(db_product, field):
                setattr(db_product, field, value)
        
        db_product.updated_at = datetime.utcnow()
        session.add(db_product)
        session.commit()
        session.refresh(db_product)
        return db_product
    
    def update_active_status(
        self, 
        product_id: uuid.UUID, 
        is_active: bool, 
        session: Session
    ) -> Optional[Product]:
        db_product = self.get_by_id(product_id, session)
        if db_product:
            db_product.is_active = is_active
            db_product.updated_at = datetime.utcnow()
            session.add(db_product)
            session.commit()
            session.refresh(db_product)
        return db_product
    
    def update_quantity(
        self,
        product_id: uuid.UUID,
        new_quantity: float,
        session: Session
    ) -> Optional[Product]:
        db_product = self.get_by_id(product_id, session)
        if db_product:
            db_product.quantity = new_quantity
            db_product.updated_at = datetime.utcnow()
            session.add(db_product)
            session.commit()
            session.refresh(db_product)
        return db_product


product_repository = ProductRepository()

