from fastapi import APIRouter, Depends

from app.api.vm.ar import r_invoice, r_aai, r_transaction, r_receipt
from app.utils.u_auth_py import authent

arRouter = APIRouter()

arRouter.include_router(r_invoice.router, prefix="/invoice",  tags=["xai_ar"], dependencies=[Depends(authent)])
arRouter.include_router(r_aai.router, prefix="/aai",  tags=["xai_aai"], dependencies=[Depends(authent)])
arRouter.include_router(r_transaction.router, prefix="/transaction",  tags=["xai_transaction"], dependencies=[Depends(authent)])
arRouter.include_router(r_receipt.router, prefix="/receipt",  tags=["xai_receipt"], dependencies=[Depends(authent)])
