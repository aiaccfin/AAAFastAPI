from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, Header, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

from sqlmodel import Session, select

from app.db import conn, models, crud
from app.utils import u_auth_py

router = APIRouter()

@router.get("/test")
def root(): return {"Biz User": "User Setup"}

@router.get("/")
def get_all(_db: Session = Depends(conn.get_session),):
    users = _db.exec(select(models.Biz_User)).all()
    if not users:
        raise HTTPException(status_code=404, detail="No users found")
    return users


@router.post("/register")
def register_user(user: models.UserCreate, _db: Session = Depends(conn.get_session)):
    o_user = crud.UserClass(_db)
    db_user = o_user.get_user_by_username(user.username)
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    return o_user.create_user(user=user)


@router.post("/token")
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), _db: Session = Depends(conn.get_session)):
    user = u_auth_py.authenticate_user(form_data.username, form_data.password, _db)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=30)

    user_data = {
        "u_name":   user.username,
        "u_bizid":  user.biz_id,
        "u_pgid":   user.primary_group_id,
        "u_prid":   user.primary_role_id 
    }
    
    access_token = u_auth_py.encode_jwt(
        data    =   user_data,
        expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/verify-token")
async def verify_user_token(authorization: str = Header(None)):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=403, detail="Invalid or missing token")

    token = authorization.split(" ")[1]
    payload = u_auth_py.verify_token(token=token)  # Validate the token
    return payload


@router.get("/samegid")
def get_all_users_same_gid(payload: dict = Depends(u_auth_py.verify_token), _db: Session = Depends(conn.get_session)):
    # Query users where their group_id matches the one extracted from the token
    group_id = payload.get("u_pgid")
    users = _db.exec(select(models.Biz_User).where(models.Biz_User.primary_group_id == group_id)).all()
    return users
