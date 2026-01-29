from sqlalchemy.orm import Session
from app.db.model.model_coa import User, Role, Permission
from .schemas import UserCreate

def create_user(db: Session, user: UserCreate, hashed_password: str):
    db_user = User(username=user.username, email=user.email, password_hash=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def create_role(db: Session, name: str):
    db_role = Role(name=name)
    db.add(db_role)
    db.commit()
    db.refresh(db_role)
    return db_role
