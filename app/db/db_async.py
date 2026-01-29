# db.py
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession,async_sessionmaker,create_async_engine

from app.config import get_settings_singleton
settings = get_settings_singleton()

dbengine = create_async_engine(
    settings.DB_ASYNC,
    pool_pre_ping=True,
    echo=False,  # True only in local dev
)

AsyncSessionLocal = async_sessionmaker(
    dbengine,
    expire_on_commit=False,
)

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        yield session