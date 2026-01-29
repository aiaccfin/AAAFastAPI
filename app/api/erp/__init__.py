from fastapi import APIRouter, Depends

from app.api.erp.product import r_product, r_item
from app.api.erp.hr import r_hr, r_workers
from app.utils.u_auth_py import authent

erpRouter = APIRouter()

erpRouter.include_router(r_product.router, prefix="/r_product", tags=["erp_product"], dependencies=[Depends(authent)])
erpRouter.include_router(r_item.router, prefix="/r_item", tags=["erp_item"], dependencies=[Depends(authent)])
erpRouter.include_router(r_workers.router, prefix="/r_workers", tags=["erp_workers"], dependencies=[Depends(authent)])
erpRouter.include_router(r_hr.router, prefix="/r_hr", tags=["erp_hr"], dependencies=[Depends(authent)])
