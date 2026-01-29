from fastapi import APIRouter

router = APIRouter()

@router.get('/test')
async def root(): return {"xAIBooks": "New View Step by Step a, FastAPI!"}
