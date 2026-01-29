from typing  import Optional, List
from fastapi import APIRouter, Depends
# from app.db  import crud_coa
# from app.schemas.coa_schema import COA

router = APIRouter()

@router.get('/test')
async def root(): return {"COA": "New View Step by Step a, FastAPI!"}

# @router.get("/")
# async def get_all_coa(limit: Optional[int] = 10, offset: Optional[int] = 0):
#     return await crud_coa.get_all_default_coa(limit, offset)


# @router.post("/")
# async def insert_coa(coa: COA):
#     return await crud_coa.insert_user(user)
