from fastapi import APIRouter, Depends

from app.api.v6.naics import p_naics
from app.api.v6.invoice import p_invoice
from app.api.v6.receipt import p_receipt
from app.api.v6.tax import p_tax
from app.api.v6.bs import p_bs
from app.api.v6.classification import ai_classification
from app.utils.u_auth_py import authent

v6Router = APIRouter()

v6Router.include_router(p_bs.router, prefix="/p_bank_statement", tags=["v6_bs"], dependencies=[Depends(authent)])
v6Router.include_router(p_tax.router, prefix="/p_tax", tags=["v6_tax"], dependencies=[Depends(authent)])
v6Router.include_router(p_receipt.router, prefix="/p_receipt", tags=["v6_receipt"], dependencies=[Depends(authent)])
v6Router.include_router(p_naics.router, prefix="/p_naics", tags=["v6_naics"], dependencies=[Depends(authent)])
# v6Router.include_router(p_invoice.router, prefix="/p_invoice", tags=["v6_invoice"], dependencies=[Depends(authent)])
v6Router.include_router(ai_classification.router, prefix="/ai_classification", tags=["v6_classification"], dependencies=[Depends(authent)])
