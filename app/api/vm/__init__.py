from fastapi import APIRouter, Depends

from app.api.vm.user import userRouter
# from app.api.vm.ar import arRouter
# from app.api.vm.docman import docRouter
# from app.utils.u_auth_py import authent

vmRouter = APIRouter()

# vmRouter.include_router(arRouter)
# vmRouter.include_router(docRouter)
vmRouter.include_router(userRouter)

