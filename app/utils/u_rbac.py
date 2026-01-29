from fastapi import HTTPException, Security, Depends
from fastapi.security import HTTPBearer
from app.database import users_collection
from app.utils.auth import verify_jwt

security = HTTPBearer()

async def get_current_user(token: str = Security(security)):
    """Extracts user info from JWT token and fetches user from DB."""
    payload = verify_jwt(token.credentials)
    user = await users_collection.find_one({"email": payload["email"]})
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    return user

def role_required(required_roles: list):
    """Decorator to check if user has required role(s)."""
    async def role_checker(user: dict = Depends(get_current_user)):
        user_roles = user.get("roles", [])
        if not any(role in user_roles for role in required_roles):
            raise HTTPException(status_code=403, detail="Forbidden: Insufficient permissions")
        return user
    return role_checker

async def check_permission(role: str, required_module: str):
    role_data = await roles_collection.find_one({"name": role})
    if required_module not in role_data["modules"]:
        raise HTTPException(status_code=403, detail="Access denied")
