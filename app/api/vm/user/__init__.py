from fastapi import APIRouter, Depends

from app.api.vm.user import r_group, r_role, r_user_new, r_user_login, r_user_delete
from app.utils.u_auth_py import authent

userRouter = APIRouter()

userRouter.include_router(r_user_login.router, prefix="/user",  tags=["p1_User"], dependencies=[Depends(authent)])
userRouter.include_router(r_user_new.router,   prefix="/user",  tags=["p1_User"], dependencies=[Depends(authent)])
userRouter.include_router(r_user_delete.router, prefix="/user",  tags=["p1_User"], dependencies=[Depends(authent)])

# userRouter.include_router(r_role.router, prefix="/role",  tags=["p1_Role"], dependencies=[Depends(authent)])
# userRouter.include_router(r_group.router,prefix="/group", tags=["p1_Group"],dependencies=[Depends(authent)])