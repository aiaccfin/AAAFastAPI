from pydantic import BaseModel, EmailStr, Field
from typing import List, Optional

# Define TokenResponse model
class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    roles: list[str]
    groups: list[str]

class LoginRequest(BaseModel):
    email: str
    password: str


class LoginVerification(BaseModel):
    email: EmailStr
    code: str