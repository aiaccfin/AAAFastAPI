from fastapi import APIRouter, Depends

from app.api.vm.docman import r_doc
from app.utils.u_auth_py import authent

docRouter = APIRouter()

docRouter.include_router(r_doc.router, prefix="/doc",  tags=["xai_document_management"], dependencies=[Depends(authent)])
