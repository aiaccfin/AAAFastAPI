# Create access token
from fastapi import Depends, HTTPException,status
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt

from app.utils import u_hash
from app.db import models

import dotenv
CFG = dotenv.dotenv_values(".env")
SECRET_KEY  = CFG['SECRET_KEY']
ALGORITHM   = CFG['ALGORITHM']


# oauth2_scheme = OAuth2PasswordBearer(tokenUrl="http://localhost:8080/biz_setup/biz_setup_user/token")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="http://99.79.70.8:8080/biz_setup/biz_setup_user/token")


def encode_jwt(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


# Authenticate the user
def authenticate_user(username: str, password: str, _db: Session):
    user = _db.query(models.Biz_User).filter(models.Biz_User.username == username).first()
    if not user:
        return False
    if not u_hash.pwd_context.verify(password, user.hashed_password):
        return False
    return user


def verify_token(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("u_name")
        if username is None:
            raise HTTPException(status_code=403, detail="Token is invalid or expired")
        return payload
    except JWTError:
        raise HTTPException(status_code=403, detail="Token is invalid or expired")


def authent():    return True
