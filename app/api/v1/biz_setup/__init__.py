from fastapi import APIRouter, Depends

from app.utils.u_auth_py import authent
from app.api.v1.biz_setup import r_biz_setup_entity, r_biz_setup_bank, r_biz_setup_user

router = APIRouter()


router.include_router(r_biz_setup_entity.router,  prefix="/biz_setup_entity", tags=["Biz Setup: Entity"], dependencies=[Depends(authent)])
router.include_router(r_biz_setup_bank.router,    prefix="/biz_setup_bank",   tags=["Biz Setup: Bank"], dependencies=[Depends(authent)])
router.include_router(r_biz_setup_user.router,    prefix="/biz_setup_user",   tags=["Biz Setup: User"], dependencies=[Depends(authent)])

@router.get("/")
def root(): return {"r_biz_SS": "Biz Setup"}
