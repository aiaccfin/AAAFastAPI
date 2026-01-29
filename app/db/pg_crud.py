from sqlalchemy.orm import Session
from . import pg_conn, pg_table
from schemas import t_schema

def get_item(db: Session, item_id: int):
    return db.query(pg_table.Item).filter(pg_table.Item.id == item_id).first()

def get_items(db: Session, skip: int = 0, limit: int = 10):
    return db.query(pg_table.Item).offset(skip).limit(limit).all()

def create_item(db: Session, item: t_schema.ItemCreate):
    db_item = pg_table.Item(name=item.name, description=item.description)
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item