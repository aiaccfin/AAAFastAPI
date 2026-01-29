# db_asyncpg.py
import os, dotenv
from app.config import settings


import asyncpg
from fastapi import HTTPException

class AsyncDatabase:
    def __init__(self):
        self.database_url = settings.CFG['PG_AWS_FASTAPI']
        

    async def connect(self):
        """Create a connection pool to the database."""
        try:
            self.pool = await asyncpg.create_pool(self.database_url)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Database connection failed: {e}")
        
    async def disconnect(self):
        self.pool.close()  
        
db = AsyncDatabase()