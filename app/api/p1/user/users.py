from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from app.db.connection.conn_rls import tenant_session_dependency
from app.models.rls.m_user_rls import UserCreate, UserRead, UserTable
from app.services.service_user import user_service

router = APIRouter()
TENANT_ID = "550e8400-e29b-41d4-a716-446655440000"
ROLE_ID = "112"
USER_ID = "111"


@router.get("/", response_model=list[UserRead])
async def list_users(session: Session = Depends(tenant_session_dependency(TENANT_ID))):
    return user_service.list_users(session)


@router.post("/", response_model=UserRead)
async def create_user(    data: UserCreate,    session: Session = Depends(tenant_session_dependency(TENANT_ID))):
   
    # Make SQLModel instance
    new_user = UserTable(**data.dict(), tenant_id=TENANT_ID)

    session.add(new_user)
    session.commit()
    session.refresh(new_user)

    return new_user
