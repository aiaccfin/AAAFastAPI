from fastapi import APIRouter, Depends

# from app.api.v7 import endpoint_invoice
from app.utils.u_auth_py import authent
from app.api.v7 import endpoint_salestax

v7Router = APIRouter()

# v7Router.include_router(endpoint_invoice.router, prefix="/invoice", tags=["v7_invoice"], dependencies=[Depends(authent)])
v7Router.include_router(endpoint_salestax.router, prefix="/salestax", tags=["v7_salestax"], dependencies=[Depends(authent)])
