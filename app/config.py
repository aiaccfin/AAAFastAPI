# app/core/config.py

import os
import secrets
from typing import ClassVar, Literal
from dotenv import load_dotenv, dotenv_values
from pydantic_settings import BaseSettings
from functools import lru_cache

# -----------------------------
# Load .env for old code
# -----------------------------
load_dotenv(".env")  # populate os.environ
ENV_VARS = dotenv_values(".env")  # keep dict for legacy usage

# -----------------------------
# BaseSettings definition
# -----------------------------
class Settings(BaseSettings):
    PROJECT_NAME: str = f"xAIBooks API - {os.getenv('ENV', 'development').capitalize()}"
    DESCRIPTION: str = "AAAA - Ai Automatic Accounting API:  production-ready"
    ENV: Literal["development", "staging", "production"] = "development"
    VERSION: str = "V2.11.18"
    SECRET_KEY: str = secrets.token_urlsafe(32)
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8
    API_USERNAME: str = "tEnangIN"
    API_PASSWORD: str = "8t>1pTu4lGTwiY3()?`+WyI|*21z"

    # Database
    # DB_ASYNC: str = "postgresql+asyncpg://postgres:password@localhost/invoicedb"
    # DB_SYNC: str = "postgresql://postgres:password@localhost/invoicedb"
    DB_ASYNC: str = "postgresql+asyncpg://postgres:postgrespwd@34.130.233.222:8000/xairls"
    DB_SYNC: str = 'postgresql://postgres:postgrespwd@34.130.233.222:8000/xairls'
    DB_POOL_SIZE: int = 5
    DB_MAX_OVERFLOW: int = 10

    PG_AIACC: str = "postgresql+asyncpg://postgres:password@localhost/aiaccdb"
    PG_RLS: str = "postgresql+asyncpg://postgres:password@localhost/rlsdb"
    PG_RLS_POSTGRES: str = "postgresql+asyncpg://postgres:password@localhost/rlsdb_postgres"
    OPENAI_API_KEY: str = "your-openai-api-key"
    PG_AWS_FASTAPI: str = "postgresql+asyncpg://postgres:password@localhost/aws_fastapi_db"
    PG_POSTGRES: str = "postgresql+asyncpg://postgres:password@localhost/postgres_db"
    MONGOL_AIACC: str = "mongodb://localhost:27017/aiacc_mongo_db"
    GOOGLE_CLOUD_API_KEY: str = "your-google-cloud-api-key"
    GOOGLE_VISION_ENDPOINT: str = "https://vision.googleapis.com/v1/images:annotate"
    MONGO_AIACCFIN: str = "mongodb://localhost:27017/aiaccfin_mongo_db"

    # Keep legacy dotenv dict
    CFG: ClassVar = ENV_VARS

    class Config:
        env_file = ".env"
        case_sensitive = True

# -----------------------------
# Singleton for new async DI usage
# -----------------------------
@lru_cache()
def get_settings_singleton() -> Settings:
    return Settings()

# -----------------------------
# Global settings object for old code
# -----------------------------
settings = get_settings_singleton()
