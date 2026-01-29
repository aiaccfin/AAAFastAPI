from fastapi import APIRouter, Depends

from app.api.v2 import r_dashboard, r_financial_reporting, r_journal, r_reconciliation, r_user, naics_router
from app.utils.u_auth_py import authent

v2Router = APIRouter()

v2Router.include_router(r_dashboard.router, prefix="/dashboard",  tags=["xai_system"], dependencies=[Depends(authent)])
v2Router.include_router(r_financial_reporting.router,   prefix="/fs",  tags=["xai_fs"], dependencies=[Depends(authent)])
v2Router.include_router(r_journal.router, prefix="/journal",  tags=["xai_journal"], dependencies=[Depends(authent)])
v2Router.include_router(r_reconciliation.router,prefix="/recon", tags=["xai_recon"],dependencies=[Depends(authent)])
v2Router.include_router(r_user.router,prefix="/thirdparty", tags=["xai_thirdparty"],dependencies=[Depends(authent)])
# v2Router.include_router(naics_router.router,prefix="/naics", tags=["xai_naics"],dependencies=[Depends(authent)])
