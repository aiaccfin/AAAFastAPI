import os
import pytest
import pytest_asyncio
from motor.motor_asyncio import AsyncIOMotorClient

from app.main import create_app
from app.config import test_settings
from app.utils import u_auth_py
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def pytest_sessionstart(session):
    logger.info("hello conftest")


@pytest_asyncio.fixture(scope="session")
async def test_db():
    """Initialize MongoDB client for test database."""
    MONGO_URI = os.getenv("MONGO_URI")
    print(f"Connecting to MongoDB at {MONGO_URI}")  # Debugging line to check URI
    client = AsyncIOMotorClient(MONGO_URI)
    db = client["test"]  # use a test database
    yield db
    client.close()

