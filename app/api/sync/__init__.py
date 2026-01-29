from fastapi import APIRouter, Depends

from app.api.sync.bs import sync_bs
from app.utils.u_auth_py import authent

syncRouter = APIRouter()

syncRouter.include_router(sync_bs.router, prefix="/sync_bs", tags=["sync"], dependencies=[Depends(authent)])
