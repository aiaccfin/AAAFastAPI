# conn_sqlalchemy.py 
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from app.config import settings


SQLALCHEMY_DATABASE_URL = settings.CFG['PG_AWS_FASTAPI']

engine = create_engine(SQLALCHEMY_DATABASE_URL) #engine that connects to the database using the provided URL.
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine) #session factory that allows us to create new database sessions for each request
Base = declarative_base()       #base class that our ORM models will inherit from.

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
        
# 1. set up the DATABASE connection